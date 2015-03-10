package main

import (
	"encoding/json"
	"io/ioutil"
	"strings"
)

type Askfm struct {
	Answer   string `json:"answer"`
	Url      string `json:"url"`
	Question string `json:"question"`
}

func Normalize(s string) string {
  ret := s
  ret = strings.TrimSpace(ret)
  ret = strings.Replace(ret, "\n", " ", -1)
  return ret
}

func main() {
	data, err := ioutil.ReadFile("qa.json")
	if err != nil {
		panic(err)
	}
	var askfm []Askfm
  err = json.Unmarshal(data, &askfm)
	if err != nil {
		panic(err)
	}
	for i := range askfm {
		askfm[i].Answer = Normalize(askfm[i].Answer)
		askfm[i].Url = Normalize(askfm[i].Url)
		askfm[i].Question = Normalize(askfm[i].Question)
	}
	b, err := json.Marshal(askfm)
	if err != nil {
		panic(err)
	}
  err = ioutil.WriteFile("qa_trim.json", b, 0644)
	if err != nil {
		panic(err)
	}
}
