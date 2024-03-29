<?php


//******  Autenticação   *********
$client_id = "EpmRestApiClient";
$client_secret = "B39C3503-C374-3227-83FE-EEA7A9BD1FDC";
$tokenUrl = "http://localhost:44333/auth/connect/token";
$tokenContent = "grant_type=password&username=sa&password=Abcd1234";
$authorization = base64_encode("$client_id:$client_secret");
//echo "$authorization \n";
$tokenHeaders = array("Authorization: Basic {$authorization}","Content-Type: application/x-www-form-urlencoded");
$token = curl_init();
curl_setopt($token, CURLOPT_URL, $tokenUrl);
curl_setopt($token, CURLOPT_HTTPHEADER, $tokenHeaders);
curl_setopt($token, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($token, CURLOPT_RETURNTRANSFER, true);
curl_setopt($token, CURLOPT_POST, true);
curl_setopt($token, CURLOPT_POSTFIELDS, $tokenContent);
$response = curl_exec($token);
curl_close ($token);
//echo "Token" . $response;
$token_array = json_decode($response, true);
//print_r($token_array);
//echo "\n now calling $url \n";
$headers = array('Content-Type: application/json',"Authorization: Bearer {$token_array["access_token"]}");

// **********  GET  ***********
$url="http://127.0.0.1:44332/epm/v1/BV/Random1";
$process = curl_init();
curl_setopt($process, CURLOPT_URL, $url);
curl_setopt($process, CURLOPT_HTTPHEADER, $headers);
curl_setopt($process, CURLOPT_CUSTOMREQUEST, "GET");
curl_setopt($process, CURLOPT_HEADER, 1);
curl_setopt($process, CURLOPT_TIMEOUT, 30);
curl_setopt($process, CURLOPT_HTTPGET, 1);
//curl_setopt($process, CURLOPT_VERBOSE, 1);
curl_setopt($process, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($process, CURLOPT_RETURNTRANSFER, TRUE);
$return = curl_exec($process);
curl_close($process);
echo $return;

// ***** POST ********

// API URL
$url = 'http://localhost:44332/opcua/v1/read';

// Create a new cURL resource
$ch = curl_init($url);

// Setup request to send json via POST
$payload = '{    
    "items": [
      {
        "path": {
          "language": "OPCUA.BrowsePath",          
          "path": "/1:BasicVariables/1:Random1"
        },
        "attributeId": 13
      }
    ]
  }';

$headers = array('Content-Type: application/json','Content-Length: ' . strlen($payload),"Authorization: Bearer {$token_array["access_token"]}");


curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($process, CURLOPT_CUSTOMREQUEST, "POST");

curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($process, CURLOPT_HEADER, 1);
curl_setopt($process, CURLOPT_TIMEOUT, 30);

// Return response instead of outputting
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Execute the POST request
$result = curl_exec($ch);

echo $result;

// Close cURL resource
curl_close($ch);


?>
