package main

import (
	"fmt"
	"math/rand/v2"
	"time"
)

func number(c chan int) {

	randNum := rand.IntN(15)
	time.Sleep(time.Duration(randNum) * time.Second)
	fmt.Printf("Function number() with sleep %d seconds is done. \n", randNum)
	c <- randNum

}

func printSlice(s []int) {
	fmt.Printf("len=%d cap=%d %v\n", len(s), cap(s), s)
}

func main() {

	c := make(chan int)
	for i := range 2 {
		fmt.Printf("Iteration: %d \n", i)
		go number(c)
	}

	var s []int
	for i := range 2 {
		fmt.Printf("Consume Iteration: %d \n", i)
		s = append(s, <-c)
	}

	printSlice(s)
}
