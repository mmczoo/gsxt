package main

import "testing"

func TestConfig(t *testing.T) {
	c := NewConfig("config.json")
	t.Logf("%+v\n", c)
}
