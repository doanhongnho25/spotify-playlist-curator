import { useEffect, useRef } from "react";

export const useInterval = (callback: () => void, delay: number | null) => {
  const savedCallback = useRef<() => void>();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) return undefined;
    const handler = () => savedCallback.current?.();
    const id = window.setInterval(handler, delay);
    return () => window.clearInterval(id);
  }, [delay]);
};
