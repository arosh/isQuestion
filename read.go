package main

import (
  "fmt"
	"encoding/json"
	"io/ioutil"
  "flag"
  "os"
)

type Askfm struct {
	Answer   string `json:"answer"`
	Url      string `json:"url"`
	Question string `json:"question"`
}

func main() {
  index := flag.Int("index", -1, "index of QA")
  flag.Parse()
  if *index == -1 {
    flag.PrintDefaults()
    os.Exit(1)
  }
	data, err := ioutil.ReadFile("qa_trim.json")
	if err != nil {
		panic(err)
	}
	var askfm []Askfm
	err = json.Unmarshal(data, &askfm)
	if err != nil {
		panic(err)
	}
  if len(askfm) <= *index {
    fmt.Fprintln(os.Stderr, "index out of range")
    os.Exit(1)
  }
  fmt.Println(askfm[*index].Question)
  fmt.Println(askfm[*index].Answer)
}
