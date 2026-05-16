import type { Stage } from "@/lib/types";
import { STAGE_COLOR, STAGE_EMOJI } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface Props {
  stage: Stage;
  className?: string;
}

export default function StageBadge({ stage, className }: Props) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
        STAGE_COLOR[stage],
        className
      )}
    >
      {STAGE_EMOJI[stage]} {stage}
    </span>
  );
}
