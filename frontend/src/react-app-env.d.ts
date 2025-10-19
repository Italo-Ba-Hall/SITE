/// <reference types="react-scripts" />

/**
 * Type declarations for lite-youtube web component
 */
declare namespace JSX {
  interface IntrinsicElements {
    'lite-youtube': React.DetailedHTMLProps<
      React.HTMLAttributes<HTMLElement> & {
        videoid: string;
        videotitle?: string;
        autoload?: string;
        params?: string;
        posterquality?: string;
        nocookie?: string;
      },
      HTMLElement
    >;
  }
}