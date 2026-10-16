package httpapi

import (
	"context"
	"fmt"
	"net/http"
	"sort"

	"github.com/redis/go-redis/v9"
)

type regionItem struct {
	Code string `json:"code"`
	Name string `json:"name"`
}

func registerRegionRoutes(mux *http.ServeMux, client *redis.Client) {
	mux.HandleFunc("POST /region/init", func(w http.ResponseWriter, r *http.Request) {
		if err := ensureRegionData(r.Context(), client); err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		writeJSON(w, http.StatusOK, map[string]any{"code": 200, "message": "region data initialized"})
	})
	mux.HandleFunc("GET /region/provinces", func(w http.ResponseWriter, r *http.Request) {
		if err := ensureRegionData(r.Context(), client); err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		items, err := readRegionSet(r.Context(), client, "region:provinces:set", "region:province:%s:info")
		if err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		regionResponse(w, items)
	})
	mux.HandleFunc("GET /region/cities", func(w http.ResponseWriter, r *http.Request) {
		provinceCode := r.URL.Query().Get("province_code")
		if provinceCode == "" {
			bad(w, "province_code is required")
			return
		}
		if err := ensureRegionData(r.Context(), client); err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		exists, err := client.SIsMember(r.Context(), "region:provinces:set", provinceCode).Result()
		if err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		if !exists {
			notFound(w, fmt.Sprintf("province code %s not found", provinceCode))
			return
		}
		items, err := readRegionSet(r.Context(), client, "region:province:"+provinceCode+":cities:set", "region:city:%s:info")
		if err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		regionResponse(w, items)
	})
	mux.HandleFunc("GET /region/districts", func(w http.ResponseWriter, r *http.Request) {
		cityCode := r.URL.Query().Get("city_code")
		if cityCode == "" {
			bad(w, "city_code is required")
			return
		}
		if err := ensureRegionData(r.Context(), client); err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		exists, err := client.Exists(r.Context(), "region:city:"+cityCode+":info").Result()
		if err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		if exists == 0 {
			notFound(w, fmt.Sprintf("city code %s not found", cityCode))
			return
		}
		items, err := readRegionSet(r.Context(), client, "region:city:"+cityCode+":districts:set", "region:district:%s:info")
		if err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"detail": "region cache unavailable"})
			return
		}
		regionResponse(w, items)
	})
}

func regionResponse(w http.ResponseWriter, items []regionItem) {
	message := "查询成功"
	if len(items) == 0 {
		message = "暂无数据"
	}
	writeJSON(w, http.StatusOK, result{Code: 200, Message: message, Data: items})
}

func readRegionSet(ctx context.Context, client *redis.Client, setKey, infoTemplate string) ([]regionItem, error) {
	codes, err := client.SMembers(ctx, setKey).Result()
	if err != nil {
		return nil, err
	}
	sort.Strings(codes)
	items := make([]regionItem, 0, len(codes))
	for _, code := range codes {
		name, err := client.HGet(ctx, fmt.Sprintf(infoTemplate, code), "name").Result()
		if err == redis.Nil {
			continue
		}
		if err != nil {
			return nil, err
		}
		items = append(items, regionItem{Code: code, Name: name})
	}
	return items, nil
}

func ensureRegionData(ctx context.Context, client *redis.Client) error {
	if err := client.Ping(ctx).Err(); err != nil {
		return err
	}
	exists, err := client.Exists(ctx, "region:provinces:set").Result()
	if err != nil || exists > 0 {
		return err
	}
	provinces := map[string]string{"110000": "北京市", "120000": "天津市", "130000": "河北省", "310000": "上海市", "320000": "江苏省", "330000": "浙江省", "440000": "广东省"}
	cities := map[string]map[string]string{"110000": {"110100": "北京市"}, "120000": {"120100": "天津市"}, "130000": {"130100": "石家庄市", "130200": "唐山市", "130300": "秦皇岛市"}, "310000": {"310100": "上海市"}, "320000": {"320100": "南京市", "320200": "无锡市", "320500": "苏州市"}, "330000": {"330100": "杭州市", "330200": "宁波市", "330300": "温州市"}, "440000": {"440100": "广州市", "440300": "深圳市", "440400": "珠海市"}}
	districts := map[string]map[string]string{"110100": {"110101": "东城区", "110102": "西城区", "110105": "朝阳区", "110106": "丰台区"}, "320100": {"320102": "玄武区", "320104": "秦淮区", "320105": "建邺区", "320106": "鼓楼区"}, "330100": {"330102": "上城区", "330105": "拱墅区", "330106": "西湖区", "330108": "滨江区"}, "440100": {"440103": "荔湾区", "440104": "越秀区", "440105": "海珠区", "440106": "天河区"}}
	pipe := client.Pipeline()
	for code, name := range provinces {
		pipe.SAdd(ctx, "region:provinces:set", code)
		pipe.HSet(ctx, "region:province:"+code+":info", "code", code, "name", name)
	}
	for province, values := range cities {
		for code, name := range values {
			pipe.HSet(ctx, "region:city:"+code+":info", "code", code, "name", name)
			pipe.SAdd(ctx, "region:province:"+province+":cities:set", code)
		}
	}
	for city, values := range districts {
		for code, name := range values {
			pipe.HSet(ctx, "region:district:"+code+":info", "code", code, "name", name)
			pipe.SAdd(ctx, "region:city:"+city+":districts:set", code)
		}
	}
	_, err = pipe.Exec(ctx)
	return err
}
