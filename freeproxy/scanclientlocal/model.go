package main

import "log"

type Model struct {
	Conf *Config
}

func NewModel(conf *Config) *Model {
	if conf == nil {
		log.Fatal("config fail!")
		return nil
	}

	return &Model{
		Conf: conf,
	}
}
