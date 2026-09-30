# Scoring

Each case expects one decision: simplify, reject, or skip.

Primary metrics are unsafe acceptance, trap rejection, ambiguous skip, safe recall, and unnecessary edit rate. A forbidden rewrite is a safety failure.

Safety regressions outrank recall gains. Record runtime, tool calls, and tokens only when measurements are comparable.