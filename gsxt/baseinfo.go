package main

import (
	"strings"
	"time"

	"github.com/xlvector/dlog"
)

type BaseInfo struct {
	CreditId string
	FirmName string
	FirmType string
	LegalRep string

	RegCaptial    string
	Establishment time.Time
	FirmAddr      string
	BusinessStart time.Time

	BusinessEnd   time.Time
	BusinessScope string    //经营范围
	RegAuthority  string    //登记机关
	ApproveData   time.Time //核准日期

	RegStatus string //登记状态
}

func NewBaseInfo(creditId, firmName, firmType, legalRep,
	regCaptial, establishment, firmAddr, businessStart,
	businessEnd, businessScope, regAuthority, approveData, regStatus string) *BaseInfo {

	esdate, err := time.Parse("2006年01月02日", establishment)
	if err != nil {
		esdate = ZeroTime
	}
	bstart, err := time.Parse("2006年01月02日", businessStart)
	if err != nil {
		bstart = ZeroTime
	}
	bend, err := time.Parse("2006年01月02日", businessEnd)
	if err != nil {
		bend = ZeroTime
	}
	apdate, err := time.Parse("2006年01月02日", approveData)
	if err != nil {
		apdate = ZeroTime
	}

	return &BaseInfo{
		CreditId:      creditId,
		FirmName:      firmName,
		FirmType:      firmType,
		LegalRep:      legalRep,
		RegCaptial:    strings.TrimSpace(regCaptial),
		Establishment: esdate,
		FirmAddr:      firmAddr,
		BusinessStart: bstart,
		BusinessEnd:   bend,
		BusinessScope: businessScope,
		RegAuthority:  regAuthority,
		ApproveData:   apdate,
		RegStatus:     regStatus,
	}

}

func (p *Model) InsertBaseInfo(binfo *BaseInfo) {
	dlog.Info("insert baseinfo: %v", binfo.CreditId)
	p.baseinfoCache = append(p.baseinfoCache, binfo)

	if len(p.baseinfoCache) >= BASEINFO_CACHE_SIZE {
		p.InsertBaseInfos()
	}
}

func (p *Model) InsertBaseInfos() error {
	l := len(p.baseinfoCache)
	dlog.Info("insert baseinfos: %d", l)
	if l <= 0 {
		return nil
	}
	ret := p.db.InsertBatch(p.baseinfoCache[0:l], true)

	p.baseinfoCache = p.baseinfoCache[0:0]
	if ret != nil {
		dlog.Error("insertbaseinfo: %s", ret)
	}
	return ret
}
