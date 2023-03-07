package main

import (
	"crypto/tls"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"net"
	"github.com/alyu/configparser"
	"time"
)

const timeout time.Duration = 20

func main() {
	fmt.Println("Simple get token app using real user/password")
	//read stuff from config.ini
	configparser.Delimiter = ":"
	config, err := configparser.Read("config.ini")
	if err != nil {
		log.Fatal("No config file, panic")
	}

	section, err := config.Section("api")
	if err != nil {
		log.Fatal("No api section in config")

	}
	//get env variagles
	//password base64 encoded
	passwordenv := os.Getenv("KUBE_PASSWORD")
	//username
	userenv := os.Getenv("KUBE_USER")
	//kube api endpoint
	kubeapi := os.Getenv("KUBE_API")

	//check if env vars are set
	if len(passwordenv) == 0 {
		log.Fatal("Do set the passwd env. eg: export KUBE_PASSWORD")
	}
	if len(userenv) == 0 {
		log.Fatal("Do set the user env variable. eg: export KUBE_USER=user@mail.com")
	}

	if len(kubeapi) == 0 {
		kubeapi = section.ValueOf("host")
		_ = kubeapi
	} else {
		kubeapi = os.Getenv("KUBE_API")
	}
	// call rest api call
	callapilogin(kubeapi, userenv, passwordenv)
}

func callapilogin(endpoint string, username string, password string) {
	// url for login endpoint
	loginendpoint := "/api/kube/login/"
	// debug messages
	fmt.Println("Kube endpoint:", endpoint)
	fmt.Println("Kube user:", username)
	// request
	jsonData := map[string]string{"password": password}
	jsonValue, _ := json.Marshal(jsonData)
	t := &http.Transport{
	    DialContext: (&net.Dialer{
	    Timeout: timeout * time.Second,
	    }).DialContext,
	    TLSClientConfig: &tls.Config{InsecureSkipVerify: true}}
	
	request, _ := http.NewRequest("POST", endpoint+loginendpoint+username, bytes.NewBuffer(jsonValue))
	request.Header.Set("Content-Type", "application/json")
	client := &http.Client{Transport: t}
	response, err := client.Do(request)

	if err != nil {
		fmt.Printf("The HTTP request failed with error %s\n", err)
	} else {
		data, _ := ioutil.ReadAll(response.Body)
		fmt.Println("token:", string(data))
	}
	return
}
