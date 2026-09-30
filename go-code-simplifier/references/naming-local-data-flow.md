# Naming and Local Data Flow

Names should expose a value's role in its current scope without unnecessary words.

Name length grows with scope and ambiguity. Short scopes may use i, j, n, v, ok, err, ctx, r, w. Normal business scopes prefer session, player, conn, room, result. Multiple same-type values need role qualifiers such as sourceSession/targetSession, oldState/newState, sender/receiver.

Avoid names that merely repeat static type/context: userSlice, playerObj, resultData, sessionSessionID. Prefer users, player, result, sessionID. Generic suffixes such as Data, Info, Obj, Item, Value, Helper, Util, Manager, Processor are suspicious only when removing them loses no domain meaning.

Prefer state names such as raw → decoded → normalized → validated over data → data2 → data3.

Primitive parameters should expose role when ambiguous: sessionID, roomID, playerID. Interface parameter names may improve documentation if only names change. Multiple bool parameters are a readability signal, not permission to redesign public API.

Pass 2 decides whether a purely redundant intermediate variable can be removed. This pass owns the remaining variable's name, role clarity, and scope. Reduce scope only when lifetime, closure capture, defer and evaluation remain unchanged.

Local/parameter renames are low risk. Private function/method renames require complete reference evidence. Exported identifiers default to report-only. After nontrivial renames check shadowing, closures, named returns, interfaces, reflection, tags/templates, generated code, registries and string/config dependencies. Use gopls rename when available, but do not depend on it.
