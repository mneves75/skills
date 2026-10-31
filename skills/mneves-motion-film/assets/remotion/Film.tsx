import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { C, timing } from "./film/theme";
// import one component per scene from ./film/scenes/

const SCENES: Record<string, React.FC> = {
  // title: Title,
  // demo: Demo,
  // end: End,
};

/** The film: every scene's start and length come from film/timing.json. */
export const Film: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.bg }}>
    {timing.scenes.map((scene) => {
      const Scene = SCENES[scene.id];
      if (!Scene) throw new Error(`no component for scene ${scene.id}`);
      return (
        <Sequence
          key={scene.id}
          from={scene.from}
          durationInFrames={scene.to - scene.from}
          name={scene.id}
        >
          <Scene />
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
