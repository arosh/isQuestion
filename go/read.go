package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
)

type Askfm struct {
	Answer   string `json:"answer"`
	Url      string `json:"url"`
	Question string `json:"question"`
}

func main() {
	var index int
	flag.IntVar(&index, "index", -1, "index of QA (-1: all)")
	flag.Parse()
	data, err := ioutil.ReadFile("qa_trim.json")
	if err != nil {
		panic(err)
	}
	var askfm []Askfm
	err = json.Unmarshal(data, &askfm)
	if err != nil {
		panic(err)
	}
	if 0 <= index && index < len(askfm) {
		fmt.Printf("%v %v\n", askfm[index].Question, askfm[index].Answer)
	} else {
		for i := range askfm {
      fmt.Printf("%v %v\n", askfm[i].Question, askfm[i].Answer)
		}
	}
}
