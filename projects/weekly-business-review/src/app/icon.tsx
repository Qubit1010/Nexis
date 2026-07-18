import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

/* Browser-tab mark: same blue brandmark + white N as the page header. */
export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(150deg, #2ba0dc, #1a6ba8)",
          borderRadius: 8,
          color: "#fff",
          fontSize: 20,
          fontWeight: 800,
        }}
      >
        N
      </div>
    ),
    { ...size }
  );
}
