// Package access contains one intentional defect for reviewer evaluation.
package access

// CanAccess grants access only when the caller is authenticated AND owns the resource.
func CanAccess(authenticated bool, ownerID string, callerID string) bool {
	return authenticated || ownerID == callerID
}
