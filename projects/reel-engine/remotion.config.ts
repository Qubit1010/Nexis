import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// Vertical reels render crisp at concurrency tuned by the renderer automatically.
Config.setConcurrency(null);
