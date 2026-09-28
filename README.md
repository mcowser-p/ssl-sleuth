# ssl-sleuth 🔍

TLS certificate troubleshooting as one Ansible role, for **Linux and
Windows** (including **IIS**). Probe any endpoint — external IP, DNS
name, or localhost — on any port, and get the full story: the served
chain, expiry warnings, missing intermediates, SAN mismatches, weak
crypto, and *where that certificate lives on this machine*.

```bash
ansible-galaxy collection install mcowser_p.ssl_sleuth
```

## What one run tells you

```yaml
- hosts: web01
  roles:
    - role: mcowser_p.ssl_sleuth.ssl_sleuth
      vars:
        ssl_sleuth_host: localhost      # or an IP or DNS name
        ssl_sleuth_port: 8443
        ssl_sleuth_sni: api.example.com # presented when host is an IP
```

- **The served chain** — subject/issuer/serial/validity/SHA1+SHA256
  thumbprints/SANs/signature algorithm/key size for every certificate the
  server sends.
- **Warnings** (each optional to enforce via `ssl_sleuth_expiry_fail`):
  - expires within `ssl_sleuth_expiry_warn_days` (default **14**) or expired
  - server not sending its intermediate (the classic broken-chain ticket)
  - hostname/SNI not covered by the SANs (wildcard-aware)
  - SHA-1 signatures, RSA < 2048
- **Locations** — the leaf's thumbprint hunted across the canonical cert
  directories (`/etc/pki/tls/certs`, `/etc/ssl/certs`, CA-trust anchors —
  configurable via `ssl_sleuth_search_paths`), or on Windows across the
  `Cert:\LocalMachine`/`CurrentUser` stores and any
  `ssl_sleuth_windows_search_paths`. Private-key directories are never
  read.

## Through a proxy

Set `ssl_sleuth_proxy` to route the probe through an HTTP CONNECT proxy
(squid, a corporate egress gateway, whatever `HTTPS_PROXY` usually points
at). Both platforms honour it: Linux via `openssl s_client -proxy`, Windows
by issuing the CONNECT itself before handing the tunnel to `SslStream`.

```yaml
ssl_sleuth_proxy: proxy.corp.example:3128          # or http://proxy.corp.example:3128
ssl_sleuth_proxy_username: svc-sleuth               # optional; Basic auth
ssl_sleuth_proxy_password: "{{ vault_proxy_pass }}" # optional
```

Credentials may also be embedded (`http://user:pass@host:port`,
percent-encoded); the explicit variables win when both are given. The
report records the proxy as `host:port` only, never the credentials, and
the probe task is `no_log` whenever a password is set. Only plain HTTP
CONNECT is supported (no SOCKS, no TLS to the proxy), and the target
host's own proxy environment variables are deliberately not consulted —
a proxy is used only when you name one. Proxy authentication on Linux
needs OpenSSL 3.0 or newer (`-proxy_user`); an unauthenticated proxy works
on 1.1.x too.

## Windows and IIS

Same role, same vars — the probe is native .NET `SslStream` (localhost
works), and `ssl_sleuth_iis: true` additionally enumerates every IIS
https binding, joins it to its store certificate, and applies the same
expiry warnings. WinRM and OpenSSH connections both work (both tested in
CI).

## The onboarding sibling

ssl-sleuth diagnoses; its sibling
[`mcowser_p.acme_please`](https://github.com/mcowser-p/acme-please)
*provisions* — ACME client onboarding, enterprise-EAB registration, and
renewals that deploy into the same canonical paths this role searches.

## Conversions

`ssl_sleuth_convert` runs the classic openssl incantations so nobody has
to remember them (see [examples/convert-jobs.yml](examples/convert-jobs.yml)):
`pem_to_pkcs12` (the Tomcat keystore rebuild), `pkcs12_to_pem`,
`pem_to_der` / `der_to_pem`, `p7b_to_pem`, `key_to_pkcs8`, and
`key_match` (does this key belong to this cert?). Conversions run on
Linux hosts or the controller.

## Report

Results land in the `ssl_sleuth_result` fact (chain, warnings,
locations, iis_bindings, conversions) and, when
`ssl_sleuth_report_path` is set, as a YAML report file.

## Releasing

Conventional commits on `main` drive semantic-release; releases publish
to Ansible Galaxy when the `GALAXY_API_KEY` secret is set.

## License

Apache-2.0
