import React from "react";
import { Composition } from "remotion";
import { Film } from "./Film";
import { timing } from "./film/theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Film"
        component={Film}
        durationInFrames={timing.durationFrames}
        fps={timing.fps}
        width={timing.width}
        height={timing.height}
      />
    </>
  );
};
