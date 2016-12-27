package main

import (
	"encoding/json"
	"io/ioutil"
	"os"

	"github.com/xlvector/dlog"
)

type Config struct {
	Host string `json:"host"`
	Port int    `json:"port"`
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
