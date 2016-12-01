package main

import "time"

var ZeroTime = time.Date(0, 0, 0, 0, 0, 0, 0, time.Local)

const (
	HTML_COMMENT_BEGIN = "\n<!--gsxt:"
	HTML_COMMENT_END   = "-->"
)

const (
	GSXT_DIR_ONE = "data"
	GSXT_DIR_SEC = "fail"
	GSXT_DIR_CJ  = "cj" //choujian

	GSXT_DIR_LEVEL_NUM = 6
)
