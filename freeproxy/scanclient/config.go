package main

import (
	"encoding/json"
	"io/ioutil"
	"os"

	"github.com/xlvector/dlog"
)

type Config struct {
	AddrsProtocl []string `json:"addrsprotocol"`
	Addrs        []string `json:"addrs"`
	AddrsIntv    int      `json:"addrsintv"`
	AddrsQPS     int      `json:"addrsqps"`

	BProtocl []string `json:"bprotocol"`
	BIp      []string `json:"bip"`
	BPorts   []string `json:"bports"`
	BIntv    int      `json:"bintv"`
	BQPS     int      `json:"bqps"`

	CProtocl []string `json:"cprotocol"`
	CIp      []string `json:"cip"`
	CPorts   []string `json:"cports"`
	CIntv    int      `json:"cintv"`
	CQPS     int      `json:"cqps"`
}

func NewConfig(fname string) *Config {
	f, err := os.Open(fname)
	if err != nil {
		dlog.Error("fail to open confile file! %s", fname, err)
		return nil
	}
	defer f.Close()

	data, err := ioutil.ReadAll(f)
	if err != nil {
		dlog.Error("fail to read confile file! %s", fname, err)
		return nil
	}

	p := &Config{}
	err = json.Unmarshal(data, p)
	if err != nil {
		dlog.Error("fail to unmarshal! %s", fname, err)
		return nil
	}

	return p
}
