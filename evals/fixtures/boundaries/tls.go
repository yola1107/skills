package boundaries

import (
	"crypto/tls"
	"crypto/x509"
	"errors"
)

// NewTLSConfig deliberately replaces the default verifier. It verifies the chain
// against explicit roots and the configured server identity, including resumptions.
// The result is an evaluation fixture, not a recommendation to replace default TLS verification.
func NewTLSConfig(roots *x509.CertPool, serverName string) (*tls.Config, error) {
	if roots == nil || serverName == "" {
		return nil, errors.New("explicit trust roots and server name required")
	}
	trusted := roots.Clone()
	return &tls.Config{
		MinVersion:         tls.VersionTLS12,
		ServerName:         serverName,
		InsecureSkipVerify: true, // The callback below supplies chain and identity verification.
		VerifyConnection: func(cs tls.ConnectionState) error {
			if len(cs.PeerCertificates) == 0 {
				return errors.New("missing peer certificate")
			}
			opts := x509.VerifyOptions{
				DNSName:       serverName,
				Roots:         trusted,
				Intermediates: x509.NewCertPool(),
				KeyUsages:     []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
			}
			for _, cert := range cs.PeerCertificates[1:] {
				opts.Intermediates.AddCert(cert)
			}
			_, err := cs.PeerCertificates[0].Verify(opts)
			return err
		},
	}, nil
}
