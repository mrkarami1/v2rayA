package serverObj

import (
	"encoding/json"
	"fmt"
	"net"
	"net/url"
	"strconv"
	"strings"
)

func init() {
	FromLinkRegister("hysteria2", NewHysteria2)
	FromLinkRegister("hy2", NewHysteria2)
	EmptyRegister("hysteria2", func() (ServerObj, error) {
		return new(Hysteria2), nil
	})
	EmptyRegister("hy2", func() (ServerObj, error) {
		return new(Hysteria2), nil
	})
}

type Hysteria2 struct {
	Name     string `json:"name"`
	Server   string `json:"server"`
	Port     int    `json:"port"`
	Password string `json:"password"`
	Protocol string `json:"protocol"`
	Link     string `json:"link"`

	// TLS fields
	SNI           string `json:"sni,omitempty"`
	AllowInsecure bool   `json:"allowInsecure,omitempty"`

	// Bandwidth (required for Hysteria2 congestion control)
	UpMbps   int `json:"upMbps,omitempty"`
	DownMbps int `json:"downMbps,omitempty"`

	// Obfuscation
	Obfs         string `json:"obfs,omitempty"`
	ObfsPassword string `json:"obfsPassword,omitempty"`

	// Advanced options
	Network string `json:"network,omitempty"` // tcp, udp, or empty (both)
}

func NewHysteria2(link string) (ServerObj, error) {
	return ParseHysteria2URL(link)
}

func ParseHysteria2URL(link string) (data *Hysteria2, err error) {
	u, err := url.Parse(link)
	if err != nil {
		return nil, err
	}

	portStr := u.Port()
	if portStr == "" {
		portStr = "443"
	}
	port, err := strconv.Atoi(portStr)
	if err != nil {
		return nil, err
	}

	query := u.Query()

	// Parse bandwidth
	upMbps, _ := strconv.Atoi(query.Get("up"))
	downMbps, _ := strconv.Atoi(query.Get("down"))

	// Parse insecure flag
	allowInsecure := query.Get("insecure") == "1"

	// Parse obfuscation
	obfs := query.Get("obfs")
	if obfs == "" {
		obfs = "none"
	}

	return &Hysteria2{
		Name:          u.Fragment,
		Server:        u.Hostname(),
		Port:          port,
		Password:      u.User.Username(),
		Protocol:      "hysteria2",
		Link:          link,
		SNI:           query.Get("sni"),
		AllowInsecure: allowInsecure,
		UpMbps:        upMbps,
		DownMbps:      downMbps,
		Obfs:          obfs,
		ObfsPassword:  query.Get("obfs-password"),
		Network:       query.Get("network"),
	}, nil
}

func (s *Hysteria2) Configuration(info PriorInfo) (c Configuration, err error) {
	// For sing-box core, generate native hysteria2 config
	if info.CoreVersion != nil && strings.Contains(strings.ToLower(info.CoreVersion.String()), "sing-box") {
		// Build sing-box hysteria2 outbound
		outbound := map[string]interface{}{
			"type":     "hysteria2",
			"tag":      "proxy",
			"server":   s.Server,
			"server_port": s.Port,
			"password": s.Password,
		}

		// TLS settings
		tls := map[string]interface{}{
			"enabled": true,
		}
		if s.SNI != "" {
			tls["server_name"] = s.SNI
		}
		if s.AllowInsecure {
			tls["insecure"] = true
		}
		outbound["tls"] = tls

		// Bandwidth
		if s.UpMbps > 0 {
			outbound["up_mbps"] = s.UpMbps
		}
		if s.DownMbps > 0 {
			outbound["down_mbps"] = s.DownMbps
		}

		// Obfuscation
		if s.Obfs != "" && s.Obfs != "none" {
			obfsConfig := map[string]interface{}{
				"type": s.Obfs,
			}
			if s.ObfsPassword != "" {
				obfsConfig["password"] = s.ObfsPassword
			}
			outbound["obfs"] = obfsConfig
		}

		// Network
		if s.Network != "" {
			outbound["network"] = s.Network
		}

		jsonBytes, err := json.Marshal(outbound)
		if err != nil {
			return Configuration{}, err
		}

		return Configuration{
			CoreOutbound: string(jsonBytes),
			UDPSupport:   true,
		}, nil
	}

	// Fallback: use plugin mode for v2ray/xray cores
	socks5 := url.URL{
		Scheme: "socks5",
		Host:   net.JoinHostPort("127.0.0.1", strconv.Itoa(info.PluginPort)),
	}
	chain := []string{socks5.String(), s.Link}
	return Configuration{
		CoreOutbound: info.PluginObj(),
		PluginChain:  strings.Join(chain, ","),
		UDPSupport:   true,
	}, nil
}

func (s *Hysteria2) ExportToURL() string {
	// Rebuild hysteria2:// URL with all parameters
	u := url.URL{
		Scheme: "hysteria2",
		User:   url.User(s.Password),
		Host:   net.JoinHostPort(s.Server, strconv.Itoa(s.Port)),
	}

	query := url.Values{}
	if s.SNI != "" {
		query.Set("sni", s.SNI)
	}
	if s.AllowInsecure {
		query.Set("insecure", "1")
	}
	if s.UpMbps > 0 {
		query.Set("up", strconv.Itoa(s.UpMbps))
	}
	if s.DownMbps > 0 {
		query.Set("down", strconv.Itoa(s.DownMbps))
	}
	if s.Obfs != "" && s.Obfs != "none" {
		query.Set("obfs", s.Obfs)
		if s.ObfsPassword != "" {
			query.Set("obfs-password", s.ObfsPassword)
		}
	}
	if s.Network != "" {
		query.Set("network", s.Network)
	}

	u.RawQuery = query.Encode()
	u.Fragment = s.Name

	return u.String()
}

func (s *Hysteria2) NeedPluginPort() bool {
	return true
}

func (s *Hysteria2) ProtoToShow() string {
	return fmt.Sprintf("hysteria2")
}

func (s *Hysteria2) GetProtocol() string {
	return s.Protocol
}

func (s *Hysteria2) GetHostname() string {
	return s.Server
}

func (s *Hysteria2) GetPort() int {
	return s.Port
}

func (s *Hysteria2) GetName() string {
	return s.Name
}

func (s *Hysteria2) SetName(name string) {
	s.Name = name
}
