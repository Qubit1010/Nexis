import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";

/**
 * Word-by-word spring reveal in the display font.
 * Text wrapped in *asterisks* renders in brand blue (accent). The span may cover
 * multiple words, e.g. "An *org chart* for your AI".
 */
export const KineticHeadline: React.FC<{
  text: string;
  fontSize?: number;
  /** Frame (relative to the enclosing Sequence) at which the reveal begins. */
  delay?: number;
  align?: "left" | "center";
  color?: string;
}> = ({ text, fontSize = 96, delay = 0, align = "center", color = COLORS.white }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Parse *accent* spans that may cover multiple words (e.g. "*org chart*").
  // A word is accented if any of its characters sit inside an asterisk-delimited
  // span; every asterisk is stripped, even when adjacent to punctuation
  // (e.g. "*workflow*," → blue "workflow," and the accent closes correctly).
  let inAccent = false;
  const words = text.split(" ").map((raw) => {
    let word = "";
    let accent = inAccent;
    for (const ch of raw) {
      if (ch === "*") {
        inAccent = !inAccent;
        accent = accent || inAccent;
        continue;
      }
      word += ch;
    }
    return { word, accent };
  });

  // Gentle continuous drift keeps the headline alive after it settles.
  const drift = Math.sin(frame / fps * 1.1) * 5;

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: `${fontSize * 0.12}px ${fontSize * 0.26}px`,
        justifyContent: align === "center" ? "center" : "flex-start",
        textAlign: align,
        fontFamily: FONTS.display,
        fontWeight: 700,
        fontSize,
        lineHeight: 1.02,
        letterSpacing: "-0.02em",
        transform: `translateY(${drift}px)`,
      }}
    >
      {words.map(({ word, accent }, i) => {
        const enter = spring({
          frame: frame - delay - i * 3,
          fps,
          config: { damping: 200, stiffness: 120, mass: 0.7 },
        });
        const y = interpolate(enter, [0, 1], [38, 0]);
        const opacity = interpolate(enter, [0, 1], [0, 1]);

        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              transform: `translateY(${y}px)`,
              opacity,
              color: accent ? COLORS.blueLight : color,
              textShadow: accent ? `0 0 28px ${COLORS.glow}` : "none",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
