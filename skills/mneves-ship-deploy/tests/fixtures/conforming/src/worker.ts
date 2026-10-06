export default {
  async fetch(request: Request, env: { APP_COMMIT: string; APP_VERSION: string; APP_ENV: string }): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({ status: "ok", commit: env.APP_COMMIT, version: env.APP_VERSION, env: env.APP_ENV });
    }
    return new Response("not found", { status: 404 });
  },
};
