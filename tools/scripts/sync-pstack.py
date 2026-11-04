#!/usr/bin/env python3
"""Generate collections/pstack from pinned, published sources.

    tools/scripts/sync-pstack.sh <port-repo> <official-repo> [dest]

<dest>/sources.json pins, by full commit, the Claude Code port of pstack
(michael-denyer/pstack-claude) and the official upstream (cursor/plugins). The
two arguments are local clones that contain those commits. Nothing is fetched:
every Git call runs with GIT_NO_LAZY_FETCH=1, so an object a partial clone
lacks fails the run instead of being downloaded.
The run:

1. checks that every component the port pins in its upstream pin file is
   identical, on the paths the port takes, to the official commit, so the
   collection is current with upstream rather than with an older port;
2. extracts the port's skills tree at its commit with `git archive` (tracked
   files only), leaving out the paths sources.json excludes, and refuses
   symlinks and submodules;
3. applies <dest>/adaptations/*.patch in name order, refusing patches that
   create symlinks or carry binary data;
4. moves frontmatter keys outside the Agent Skills spec under `metadata:`;
5. validates the result: every skill passes the Agent Skills reference
   validator (`agentskills validate`, which must be on PATH; this script does
   not parse YAML itself), name == directory, every relative Markdown link and
   #anchor resolves inside the collection, no retired skill survives or is
   still named, no absolute home path;
6. writes UPSTREAM (every input commit and patch digest) and copies the port's
   license and notice files, then swaps the outputs into <dest>.

<dest>/skills, UPSTREAM, LICENSE* and NOTICE* are generated; README.md,
sources.json and adaptations/ are hand-written. Every check runs before the
swap, so a failed run leaves <dest> unchanged, and the same inputs always
produce the same bytes.

Python 3.11 or later, standard library only, plus the skills-ref validator's
`agentskills` command on PATH.

SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2026 Marcus Neves
"""
import fnmatch
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

SPEC_KEYS = {"name", "description", "license", "compatibility", "allowed-tools", "metadata"}
SHA = re.compile(r"^[0-9a-f]{40}$")
URL = re.compile(r"^https://[A-Za-z0-9.-]+(/[A-Za-z0-9._~/-]+)$")
# A machine's home path in a published file; documentation placeholders such as /Users/you/ pass.
HOME_PATH = re.compile(r"/(?:Users|home)/(?!(?:you|me|user|username|example|<[^>/]+>)/)[A-Za-z0-9._-]+/")


class SyncError(Exception):
    pass


# A partial clone would otherwise download a missing object on demand.
LOCAL_GIT = dict(os.environ, GIT_NO_LAZY_FETCH="1")


def git(repo, *args, binary=False):
    result = subprocess.run(["git", "-C", repo, *args], capture_output=True, env=LOCAL_GIT)
    if result.returncode:
        raise SyncError(f"git {' '.join(args[:3])} in {repo}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout if binary else result.stdout.decode()


def rel_path(value, label):
    if not isinstance(value, str) or not value or value.startswith("/") or ".." in value.split("/"):
        raise SyncError(f"sources.json: {label} must be a relative path inside the repository, got {value!r}")
    return value.strip("/")


def load_sources(dest):
    path = os.path.join(dest, "sources.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SyncError(f"{path} is missing") from None
    except json.JSONDecodeError as e:
        raise SyncError(f"{path}: {e}") from None
    if not isinstance(data, dict) or set(data) - {"port", "official", "exclude", "retired"}:
        raise SyncError("sources.json: top-level keys are port, official, exclude and retired")
    shapes = {
        "port": {"url", "commit", "skills", "manifest", "pins", "notices"},
        "official": {"url", "commit"},
    }
    for block, keys in shapes.items():
        value = data.get(block)
        if not isinstance(value, dict) or set(value) != keys:
            raise SyncError(f"sources.json: {block} needs exactly {', '.join(sorted(keys))}")
        if not isinstance(value["url"], str) or not URL.match(value["url"]):
            # The rejected value is not echoed: it may carry credentials.
            raise SyncError(f"sources.json: {block}.url must be https://<host>/<path>, with no credentials, query or fragment")
        if not isinstance(value["commit"], str) or not SHA.match(value["commit"]):
            raise SyncError(f"sources.json: {block}.commit must be a full 40-character commit, got {value['commit']!r}")
    port = data["port"]
    for key in ("skills", "manifest", "pins"):
        port[key] = rel_path(port[key], f"port.{key}")
    if not isinstance(port["notices"], list) or not port["notices"]:
        raise SyncError("sources.json: port.notices must list the license and notice files")
    port["notices"] = [rel_path(n, "port.notices") for n in port["notices"]]
    for n in port["notices"]:
        if not fnmatch.fnmatch(os.path.basename(n), "LICENSE*") and not fnmatch.fnmatch(os.path.basename(n), "NOTICE*"):
            raise SyncError(f"sources.json: notice {n!r} must be named LICENSE* or NOTICE*")
    for block in ("exclude", "retired"):
        value = data.setdefault(block, {})
        if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) and v for k, v in value.items()):
            raise SyncError(f"sources.json: {block} maps each entry to its reason")
    data["exclude"] = {rel_path(k, "exclude"): v for k, v in data["exclude"].items()}
    for name in data["retired"]:
        if not re.fullmatch(r"[a-z0-9-]+\*?", name):
            raise SyncError(f"sources.json: retired entry {name!r} must be a skill name, optionally ending in *")
    return data


def require_commit(repo, sha, label):
    probe = subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True, env=LOCAL_GIT)
    if probe.returncode:
        raise SyncError(f"{label} commit {sha} is not in {repo}; fetch it first")


def check_provenance(port_repo, official_repo, sources):
    port, official = sources["port"], sources["official"]
    try:
        pins = json.loads(git(port_repo, "show", f"{port['commit']}:{port['pins']}"))
        components = pins["components"]
    except (json.JSONDecodeError, KeyError, TypeError):
        raise SyncError(f"{port['pins']} at the port commit is not a pin file with components") from None

    def norm(url):
        return url.rstrip("/").removesuffix(".git")

    remote = str(pins.get("remote", ""))
    if norm(remote) != norm(official["url"]):
        shown = remote if URL.match(norm(remote) or "-") else "a remote that is not a plain https URL"
        raise SyncError(f"the port pins {shown}, but sources.json names {official['url']}")
    lines = []
    for name in sorted(components):
        component = components[name]
        sha, path = component.get("sha", ""), str(component.get("upstreamPath", "")).strip("/")
        if not SHA.match(sha) or not path:
            raise SyncError(f"the port's pin for {name} needs a full sha and an upstreamPath")
        require_commit(official_repo, sha, f"the port's {name} pin")
        spec = [path] + [f":(exclude){path}/{e.strip('/')}" for e in component.get("exclude", [])]
        changed = git(official_repo, "diff", "--name-only", sha, official["commit"], "--", *spec).split()
        if changed:
            raise SyncError(
                f"the port's {name} pin {sha[:12]} is behind official {official['commit'][:12]}: "
                f"{len(changed)} file(s) differ, first {changed[0]}"
            )
        lines.append(f"component: {name} {sha} {path} (identical at official-commit)")
    return lines


def extract(port_repo, sources, stage):
    port = sources["port"]
    commit, skills = port["commit"], port["skills"]
    tree = git(port_repo, "ls-tree", "-r", "--full-tree", commit, "--", skills)
    if not tree.strip():
        raise SyncError(f"the port commit has no {skills}")
    bad = [line.split("\t", 1)[1] for line in tree.splitlines() if line.split()[0] in ("120000", "160000")]
    if bad:
        raise SyncError("refusing symlinks or submodules in the port's skills:\n  " + "\n  ".join(bad))
    for path in sources["exclude"]:
        probe = subprocess.run(
            ["git", "-C", port_repo, "cat-file", "-e", f"{commit}:{skills}/{path}"], capture_output=True, env=LOCAL_GIT
        )
        if probe.returncode:
            raise SyncError(f"exclude {path!r} matches nothing in the port's skills")
    spec = [skills] + [f":(exclude){skills}/{p}" for p in sorted(sources["exclude"])]
    archive = git(port_repo, "archive", "--format=tar", commit, "--", *spec, binary=True)
    out = os.path.join(stage, "skills")
    os.mkdir(out)
    subprocess.run(["tar", "-x", "-C", out, f"--strip-components={skills.count('/') + 1}"], input=archive, check=True)
    return out


def apply_patches(dest, skills_dir):
    patches = sorted(glob.glob(os.path.join(dest, "adaptations", "*.patch")))
    # Outside any repository, git apply patches the files under its working directory; the
    # ceiling keeps it from finding the repository that holds the stage.
    env = dict(LOCAL_GIT, GIT_CEILING_DIRECTORIES=os.path.dirname(skills_dir))
    digests = []
    for patch in patches:
        name = os.path.basename(patch)
        with open(patch, "rb") as f:
            data = f.read()
        if re.search(rb"^(?:new file mode|new mode|deleted file mode|old mode) 1[26]0000", data, re.M):
            raise SyncError(f"{name} creates or changes a symlink or submodule")
        if b"GIT binary patch" in data:
            raise SyncError(f"{name} carries binary data")
        result = subprocess.run(["git", "apply", "--whitespace=nowarn", patch], cwd=skills_dir, env=env, capture_output=True)
        if result.returncode:
            raise SyncError(f"{name} does not apply:\n{result.stderr.decode(errors='replace').strip()}")
        digests.append(f"adaptation: {name} sha256:{hashlib.sha256(data).hexdigest()}")
    return digests


def normalize_frontmatter(skills_dir):
    errors = []
    for name in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not m:
            errors.append(f"{name}: no frontmatter")
            continue
        entries = []  # [key, [lines]]
        for line in m.group(1).split("\n"):
            km = re.match(r"([A-Za-z0-9_-]+):(.*)$", line)
            if km and not line.startswith((" ", "\t")):
                entries.append([km.group(1), [line]])
            elif entries:
                entries[-1][1].append(line)
            else:
                errors.append(f"{name}: unparseable frontmatter line {line!r}")
        moved, kept = [], []
        for key, lines in entries:
            if key in SPEC_KEYS:
                kept.append([key, lines])
                continue
            if len(lines) != 1:
                errors.append(f"{name}: non-spec key {key!r} spans several lines")
                continue
            value = lines[0].split(":", 1)[1].strip()
            if len(value) >= 2 and value[0] == value[-1] == "'":
                value = value[1:-1].replace("''", "'")
            elif len(value) >= 2 and value[0] == value[-1] == '"':
                try:
                    value = json.loads(value)  # YAML's common double-quoted escapes are JSON's
                except ValueError:
                    errors.append(f"{name}: cannot decode the quoted value of {key!r}")
                    continue
            moved.append((key, value))
        if not moved:
            continue
        meta = next((e for e in kept if e[0] == "metadata"), None)
        if meta is None:
            meta = ["metadata", ["metadata:"]]
            kept.append(meta)
        elif meta[1][0].strip() != "metadata:":
            errors.append(f"{name}: flow-style metadata cannot take moved keys")
            continue
        children = [line for line in meta[1][1:] if line.strip() and not line.lstrip().startswith("#")]
        indent = children[0][: len(children[0]) - len(children[0].lstrip())] if children else "  "
        meta[1].extend(f"{indent}{key}: {json.dumps(value)}" for key, value in moved)
        head = "\n".join(line for _, lines in kept for line in lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"---\n{head}\n---\n" + text[m.end():])
    return errors


def frontmatter(path):
    with open(path, encoding="utf-8") as f:
        m = re.match(r"---\n(.*?)\n---\n", f.read(), re.S)
    fields = {}
    if m:
        for line in m.group(1).split("\n"):
            km = re.match(r"([A-Za-z0-9_-]+):\s*(.*)$", line)
            if km and not line.startswith((" ", "\t")):
                value = km.group(2).strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                    value = value[1:-1]
                fields[km.group(1)] = value
    return fields


def slug(heading):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def markdown_lines(text, keep_code=False):
    """Yield (number, line) outside fenced code blocks. Inline code spans are removed, so links
    inside them are not checked; keep_code keeps their text, which a heading's anchor includes."""
    fence = None
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            if fence is None:
                fence = marker.group(1)[0] * len(marker.group(1))
            elif stripped.startswith(fence):
                fence = None
            continue
        if fence is None:
            yield number, line if keep_code else re.sub(r"`+[^`]*`+", "", line)


def anchors(path, cache):
    if path not in cache:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        seen, found = {}, set()
        for _, line in markdown_lines(text, keep_code=True):
            h = re.match(r"#{1,6}\s+(.*?)\s*#*\s*$", line)
            if h:
                base = slug(h.group(1))
                count = seen.get(base, 0)
                seen[base] = count + 1
                found.add(base if count == 0 else f"{base}-{count}")
        found.update(re.findall(r"<a\s+(?:id|name)=\"([^\"]+)\"", text))
        cache[path] = found
    return cache[path]


LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFDEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)")


def validate(skills_dir, sources):
    errors, cache = [], {}
    root = os.path.realpath(skills_dir)
    retired = sources["retired"]
    retired_res = {
        name: re.compile(r"(?<![\w-])" + re.escape(name).replace(r"\*", r"[a-z0-9-]+") + r"(?![\w-])") for name in retired
    }
    skills = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
    for name in skills:
        for pattern in retired:
            if fnmatch.fnmatch(name, pattern):
                errors.append(f"{name}: retired by sources.json ({pattern})")
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            errors.append(f"{name}: no SKILL.md")
            continue
        fields = frontmatter(path)
        if fields.get("name") != name:
            errors.append(f"{name}: frontmatter name must equal the directory name")
        if not 0 < len(fields.get("description", "")) <= 1024:
            errors.append(f"{name}: description must be 1 to 1024 characters")
        if set(fields) - SPEC_KEYS:
            errors.append(f"{name}: frontmatter keys outside the spec: {', '.join(sorted(set(fields) - SPEC_KEYS))}")
    for dirpath, dirs, files in os.walk(skills_dir):
        dirs.sort()
        for entry in sorted(dirs + files):
            if os.path.islink(os.path.join(dirpath, entry)):
                errors.append(f"{os.path.relpath(os.path.join(dirpath, entry), skills_dir)}: symlink")
        for file in sorted(files):
            path = os.path.join(dirpath, file)
            rel = os.path.relpath(path, skills_dir)
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(text.split("\n"), 1):
                for pattern, regex in retired_res.items():
                    hit = regex.search(line)
                    if hit:
                        errors.append(f"{rel}:{number}: names retired skill {hit.group(0)} ({pattern})")
                if HOME_PATH.search(line):
                    errors.append(f"{rel}:{number}: absolute home path")
            if not file.endswith(".md"):
                continue
            for number, line in markdown_lines(text):
                targets = LINK.findall(line) + REFDEF.findall(line)
                for target in targets:
                    if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                        continue  # http, https, mailto
                    where = f"{rel}:{number}: link {target}"
                    if target.startswith(("/", "~")):
                        errors.append(f"{where} is an absolute path")
                        continue
                    target_path, _, fragment = urllib.parse.unquote(target).partition("#")
                    resolved = os.path.realpath(os.path.join(dirpath, target_path)) if target_path else os.path.realpath(path)
                    if os.path.commonpath([root, resolved]) != root:
                        errors.append(f"{where} leaves the collection")
                    elif not os.path.exists(resolved):
                        errors.append(f"{where} does not resolve")
                    elif fragment and resolved.endswith(".md") and fragment not in anchors(resolved, cache):
                        errors.append(f"{where} names a missing anchor")
    return errors


def reference_validate(validator, skills_dir):
    """Run the Agent Skills reference validator on every generated skill."""
    errors = []
    for name in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, name)
        if not os.path.isdir(path):
            continue
        result = subprocess.run([validator, "validate", path], capture_output=True)
        if result.returncode:
            text = (result.stdout + result.stderr).decode(errors="replace").replace(skills_dir + os.sep, "")
            errors.append(f"{name}: agentskills validate exited {result.returncode}: " + " ".join(text.split()))
    return errors


def write_outputs(port_repo, sources, stage, header_lines, version, count):
    port = sources["port"]
    for notice in port["notices"]:
        data = git(port_repo, "show", f"{port['commit']}:{notice}", binary=True)
        with open(os.path.join(stage, os.path.basename(notice)), "wb") as f:
            f.write(data)
    lines = [
        "# Generated by tools/scripts/sync-pstack.sh from sources.json and adaptations/. Do not edit.",
        f"port: {port['url']}",
        f"port-commit: {port['commit']}",
        f"port-version: {version}",
        f"official: {sources['official']['url']}",
        f"official-commit: {sources['official']['commit']}",
        *header_lines,
        *(f"excluded: {p}" for p in sorted(sources["exclude"])),
        *(f"retired: {p}" for p in sorted(sources["retired"])),
        f"skills: {count}",
    ]
    with open(os.path.join(stage, "UPSTREAM"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def owned(directory):
    names = ["skills", "UPSTREAM", "local-overrides.patch"]
    names += [n for n in os.listdir(directory) if fnmatch.fnmatch(n, "LICENSE*") or fnmatch.fnmatch(n, "NOTICE*")]
    return sorted(n for n in set(names) if os.path.lexists(os.path.join(directory, n)))


def swap(stage, dest):
    backup = os.path.join(stage, ".previous")
    os.mkdir(backup)
    moved_out, moved_in = [], []
    try:
        for name in owned(dest):
            os.rename(os.path.join(dest, name), os.path.join(backup, name))
            moved_out.append(name)
        for name in owned(stage):
            os.rename(os.path.join(stage, name), os.path.join(dest, name))
            moved_in.append(name)
    except OSError:
        for name in moved_in:
            os.rename(os.path.join(dest, name), os.path.join(stage, name))
        for name in moved_out:
            os.rename(os.path.join(backup, name), os.path.join(dest, name))
        raise


def main(argv):
    if len(argv) not in (3, 4):
        print("usage: sync-pstack.sh <port-repo> <official-repo> [dest]", file=sys.stderr)
        return 2
    port_repo, official_repo = argv[1], argv[2]
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dest = os.path.abspath(argv[3] if len(argv) == 4 else os.path.join(repo_root, "collections", "pstack"))
    try:
        validator = shutil.which("agentskills")
        if not validator:
            raise SyncError(
                "the Agent Skills reference validator `agentskills` is not on PATH; install skills-ref as "
                "AGENTS.md describes. Nothing is published without it."
            )
        sources = load_sources(dest)
        require_commit(port_repo, sources["port"]["commit"], "port")
        require_commit(official_repo, sources["official"]["commit"], "official")
        components = check_provenance(port_repo, official_repo, sources)
        try:
            version = json.loads(git(port_repo, "show", f"{sources['port']['commit']}:{sources['port']['manifest']}"))["version"]
        except (json.JSONDecodeError, KeyError, TypeError):
            raise SyncError(f"{sources['port']['manifest']} at the port commit has no version") from None
        stage = tempfile.mkdtemp(prefix=".sync-pstack.", dir=os.path.dirname(dest))
        try:
            skills_dir = extract(port_repo, sources, stage)
            digests = apply_patches(dest, skills_dir)
            errors = normalize_frontmatter(skills_dir)
            errors += validate(skills_dir, sources)
            errors += reference_validate(validator, skills_dir)
            if errors:
                raise SyncError("the generated collection fails its checks:\n  " + "\n  ".join(errors))
            count = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])
            write_outputs(port_repo, sources, stage, components + digests, version, count)
            swap(stage, dest)
        finally:
            shutil.rmtree(stage, ignore_errors=True)
    except SyncError as e:
        print(f"sync-pstack: {e}", file=sys.stderr)
        return 1
    print(f"synced {count} skills from port {sources['port']['commit'][:12]} ({version}), official {sources['official']['commit'][:12]}, into {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
