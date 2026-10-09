package access

import "testing"

func TestCanAccessRequiresAuthenticationAndOwnership(t *testing.T) {
	cases := []struct {
		name          string
		authenticated bool
		ownerID       string
		callerID      string
		want          bool
	}{
		{name: "authenticated owner", authenticated: true, ownerID: "a", callerID: "a", want: true},
		{name: "authenticated other user", authenticated: true, ownerID: "a", callerID: "b", want: false},
		{name: "unauthenticated owner", authenticated: false, ownerID: "a", callerID: "a", want: false},
		{name: "unauthenticated other user", authenticated: false, ownerID: "a", callerID: "b", want: false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := CanAccess(tc.authenticated, tc.ownerID, tc.callerID); got != tc.want {
				t.Fatalf("CanAccess(%v, %q, %q) = %v, want %v", tc.authenticated, tc.ownerID, tc.callerID, got, tc.want)
			}
		})
	}
}
