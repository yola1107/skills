package boundaries

import (
	"context"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"math/big"
	"net"
	"testing"
	"time"
)

func testCertificate(t *testing.T, expires time.Time) (tls.Certificate, *x509.CertPool) {
	t.Helper()
	key, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		t.Fatal(err)
	}
	template := &x509.Certificate{
		SerialNumber:          big.NewInt(1),
		Subject:               pkix.Name{CommonName: "evaluation only"},
		DNSNames:              []string{"report.example"},
		NotBefore:             expires.Add(-24 * time.Hour),
		NotAfter:              expires,
		KeyUsage:              x509.KeyUsageDigitalSignature | x509.KeyUsageCertSign,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
		IsCA:                  true,
	}
	der, err := x509.CreateCertificate(rand.Reader, template, template, &key.PublicKey, key)
	if err != nil {
		t.Fatal(err)
	}
	cert, err := x509.ParseCertificate(der)
	if err != nil {
		t.Fatal(err)
	}
	roots := x509.NewCertPool()
	roots.AddCert(cert)
	return tls.Certificate{Certificate: [][]byte{der}, PrivateKey: key}, roots
}

// handshake uses an in-memory pipe, not a network listener. Every goroutine is
// joined before returning; deadlines bound a broken handshake without sleeps.
func handshake(t *testing.T, config *tls.Config, cert tls.Certificate) error {
	t.Helper()
	clientConn, serverConn := net.Pipe()
	defer clientConn.Close()
	defer serverConn.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	server := tls.Server(serverConn, &tls.Config{
		Certificates:           []tls.Certificate{cert},
		SessionTicketsDisabled: true,
	})
	serverDone := make(chan error, 1)
	go func() {
		serverDone <- server.HandshakeContext(ctx)
	}()
	client := tls.Client(clientConn, config)
	clientErr := client.HandshakeContext(ctx)
	clientConn.Close()
	serverConn.Close()
	serverErr := <-serverDone
	if clientErr == nil && serverErr != nil {
		t.Fatalf("client succeeded but server failed: %v", serverErr)
	}
	return clientErr
}

func TestTLSConfigVerifiesIdentity(t *testing.T) {
	cert, roots := testCertificate(t, time.Now().Add(time.Hour))
	expired, expiredRoots := testCertificate(t, time.Now().Add(-time.Hour))
	cases := []struct {
		name    string
		host    string
		roots   *x509.CertPool
		cert    tls.Certificate
		wantErr bool
	}{
		{name: "trusted identity", host: "report.example", roots: roots, cert: cert},
		{name: "wrong hostname", host: "other.example", roots: roots, cert: cert, wantErr: true},
		{name: "untrusted certificate", host: "report.example", roots: x509.NewCertPool(), cert: cert, wantErr: true},
		{name: "expired certificate", host: "report.example", roots: expiredRoots, cert: expired, wantErr: true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			config, err := NewTLSConfig(tc.roots, tc.host)
			if err != nil {
				t.Fatal(err)
			}
			if err = handshake(t, config, tc.cert); (err != nil) != tc.wantErr {
				t.Fatalf("handshake err=%v, wantErr=%v", err, tc.wantErr)
			}
		})
	}
}

func TestTLSConfigRejectsMissingTrust(t *testing.T) {
	if _, err := NewTLSConfig(nil, "report.example"); err == nil {
		t.Fatal("missing roots accepted")
	}
	if _, err := NewTLSConfig(x509.NewCertPool(), ""); err == nil {
		t.Fatal("missing identity accepted")
	}
	config, err := NewTLSConfig(x509.NewCertPool(), "report.example")
	if err != nil {
		t.Fatal(err)
	}
	if err = config.VerifyConnection(tls.ConnectionState{}); err == nil {
		t.Fatal("missing peer certificate accepted")
	}
}
