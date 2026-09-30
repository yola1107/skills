# Naming and Local Data Flow

Names should expose a value's role in its current scope without unnecessary words.

Name length grows with scope and ambiguity. Short scopes may use i, j, n, v, ok, err, ctx, r, w. Normal business scopes prefer session, player, conn, room, result. Multiple same-type values need role qualifiers such as sourceSession/targetSession, oldState/newState, sender/receiver.

Avoid names that merely repeat static type/context: userSlice, playerObj, resultData, sessionSessionID. Prefer users, player, result, sessionID. Generic suffixes such as Data, Info, Obj, Item, Value, Helper, Util, Manager, Processor are suspicious only when removing them loses no domain meaning.

Prefer state names such as raw → decoded → normalized → validated over data → data2 → data3.

Primitive parameters should expose role when ambiguous: sessionID, roomID, playerID. Interface parameter names may improve documentation if only names change. Multiple bool parameters are a readability signal, not permission to redesign public API.

Pass 2 decides whether a purely redundant intermediate variable can be removed. This pass owns the remaining variable's name, role clarity, and scope. Reduce scope only when lifetime, closure capture, defer and evaluation remain unchanged.

Local/parameter renames are low risk. Private function/method renames require complete reference evidence. Exported identifiers default to report-only. After nontrivial renames check shadowing, closures, named returns, interfaces, reflection, tags/templates, generated code, registries and string/config dependencies. Use gopls rename when available, but do not depend on it.


## Method receivers

Receiver names follow normal Go locality rules and should be short, meaningful, and consistent across methods of the same type.

Prefer a short abbreviation derived from the receiver type:
- `s *Server` rather than `this *Server` or `self *Server`;
- `c *Client`;
- `r *Registry`;
- `p *Player`.

Avoid `this`, `self`, `me`, and verbose repetitions such as `server *Server` when a short receiver is unambiguous.

Receiver renaming is a naming-only cleanup: do **not** change pointer receiver to value receiver, value receiver to pointer receiver, receiver type, method set, mutability, nil-receiver behavior, or interface satisfaction.

Use one receiver name consistently across methods of the same type unless a local collision makes that misleading. Before renaming, check method body shadowing and closures. Receiver names are local to method declarations, so a pure receiver-identifier rename is normally low risk when all references inside that method are updated.
