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
		askfm[i].Answer = strings.TrimSpace(askfm[i].Answer)
		askfm[i].Url = strings.TrimSpace(askfm[i].Url)
		askfm[i].Question = strings.TrimSpace(askfm[i].Question)
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
