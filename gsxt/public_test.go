package main

import "testing"

func TestBase(t *testing.T) {

	a := make([]int, 0, 10)
	a = append(a, 2)
	t.Logf("l:%d c:%d", len(a), cap(a))

	b := a[0:0]
	t.Logf("l:%d c:%d", len(b), cap(b))

}
