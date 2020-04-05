import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import './api.dart';
import './size_config.dart';

//void main() => StoreListPage();

class CartPage extends StatefulWidget {
  const CartPage({Key key}) : super(key: key);
  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return _CartPageState();
  }
}

class _CartPageState extends State<CartPage> {
  final storage = new FlutterSecureStorage();

  String _storeAcceptanceType = 'confirm_first';

  Map _storeDetails = {
    "id": 1,
    "name": "Balaji stores",
    "owner": "Someone"
  };

  List<Map> _cartItems = [
    {
      "index": 1,
      "item": "",
      "quantity": ""
    }
  ];
  @override
  void initState() {
    // TODO: implement initState
    super.initState();
//    getInitialData();
  }

  void getInitialData() async {
    Map<String, String> data = {
      "store_id": await storage.read(key: "selectedStore")
    };
    if(data["store_id"] == null) {
      print('no');
    }
    SharedPreferences prefs = await SharedPreferences.getInstance();
    var token = prefs.getString('token');
    Map<String, String> headers = {
      "Content-Type": "application/json",
      "Authorization": "token $token"
    };
    final response = await http.post(Api.url, headers: headers, body: json.encode(data));
    if(response.statusCode == 200) {
      Map responseJson = json.decode(response.body);
      if(responseJson['success'] == true) {
        setState(() {
          _storeDetails = responseJson['store'];
        });
      }
    } else {
      throw Exception("Failed to load post");
    }
  }

  Future<Map> sendCartList() async {
    var map = new Map<String, dynamic>();
    print(await storage.read(key: "selectedStore"));
    map["store_id"] = await storage.read(key: "selectedStore");
    map["cart"] = _cartItems;
    map["store_acceptance_type"] = _storeAcceptanceType;
    SharedPreferences prefs = await SharedPreferences.getInstance();
    var token = prefs.getString('token');
    Map<String, String> headers = {
      "Authorization": "token $token"
    };
    final response = await http.post(Api.url+'/api/v1/addList', headers: headers, body: map);
    if(response.statusCode == 200) {
      Map responseJson = json.decode(response.body);
      return responseJson;
    } else {
      throw Exception("Failed to load post");
    }
  }

  @override
  Widget build(BuildContext context) {
    SizeConfig().init(context);
    List<Widget> _cartItemWidgets = new List<Widget>();
    for(var _cartItem in _cartItems) {
      _cartItemWidgets.add(
          Container(
              child: Row(
                children: <Widget>[
                  Container(
                    alignment: Alignment.center,
                    width: SizeConfig.blockSizeHorizontal*8,
                    height: SizeConfig.blockSizeHorizontal*8,
                    decoration: BoxDecoration(
                      color: Color(0xff2c3e50),
                      shape: BoxShape.circle
                    ),
                    child: Text('${_cartItem["index"]}', style: TextStyle(color:Colors.white, fontWeight: FontWeight.bold)),
                  ),
                  Container(
                      width: SizeConfig.blockSizeHorizontal*55,
                      padding: EdgeInsets.symmetric(horizontal: SizeConfig.blockSizeHorizontal*2.0, vertical: SizeConfig.blockSizeVertical*2.0),
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Item',
                          contentPadding: EdgeInsets.fromLTRB(5.0, 10.0, 5.0, 10.0),
                          border: new OutlineInputBorder(
                            borderRadius: new BorderRadius.circular(5.0),
                            borderSide: new BorderSide(
                            ),
                          ),
                        ),
                        onChanged: (text) {
                          _cartItem["item"] = text;
                        },
                        controller: TextEditingController.fromValue(
                            TextEditingValue(
                                text: _cartItem["item"].toString()
                            )
                        ),
                      )
                  ),
                  Expanded(
                    child: Container(
                        padding: EdgeInsets.symmetric(horizontal: SizeConfig.blockSizeHorizontal*2.0, vertical: SizeConfig.blockSizeVertical*2.0),
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Quantity',
                          contentPadding: EdgeInsets.fromLTRB(5.0, 10.0, 5.0, 10.0),
                          border: new OutlineInputBorder(
                            borderRadius: new BorderRadius.circular(5.0),
                            borderSide: new BorderSide(
                            ),
                          ),
                        ),
                        onChanged: (text) {
                          _cartItem["quantity"] = text;
                        },
                        controller: TextEditingController.fromValue(
                            TextEditingValue(
                                text: _cartItem["quantity"].toString()
                            )
                        ),
                      )
                    )
                  )
                ],
              )
          )
      );
    }
    // TODO: implement build
    return Container(
        child: Column(
          children: <Widget>[
            Container(
              alignment: Alignment.centerLeft,
              padding: EdgeInsets.symmetric(vertical:SizeConfig.blockSizeVertical*2.0, horizontal:SizeConfig.blockSizeHorizontal*5.0),
              child: Text('Cart', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22.0)),
            ),
            Container(
              padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: <Widget>[
                  Container(
                    child: Row(
                      children: <Widget>[
                        Radio(
                          value: 'available',
                          groupValue: _storeAcceptanceType,
                          onChanged: (value) {
                            setState(() { _storeAcceptanceType = value; });
                          },
                        ),
                        Text('Give what is available')
                      ],
                    ),
                  ),
                  Container(
                      child: Row(
                        children: <Widget>[
                          Radio(
                            value: 'confirm_first',
                            groupValue: _storeAcceptanceType,
                            onChanged: (value) {
                              setState(() { _storeAcceptanceType = value; });
                            },
                          ),
                          Text('Confirm First')
                        ],
                      )
                  )
                ],
              ),
            ),
            Expanded(
              child: Container(
                padding:EdgeInsets.all(10.0),
                  child: Column(
                    children: <Widget>[
                      Expanded(
                          child: ListView(
                            shrinkWrap: true,
                            children: <Widget>[
                              Column(
                                children: _cartItemWidgets,
                              )
                            ],
                          )
                      ),
                      Material(
                          child: MaterialButton(
                            color: Color(0xff5D6D7E),
                            elevation: 2.0,
                            padding: EdgeInsets.symmetric(vertical: 10.0, horizontal: 30.0),
                            child: Text('Add Item', style: TextStyle(color: Colors.white, fontSize: 20.0)),
                            onPressed: () {
                              setState(() {
                                _cartItems.add({
                                  "index": _cartItems.length+1,
                                  "item": "",
                                  "quantity": ""
                                });
                              });
                            },
                          )
                      ),
                      Material(
                          child: MaterialButton(
                            color: Color(0xff3498DB),
                            elevation: 2.0,
                            padding: EdgeInsets.symmetric(vertical: 10.0, horizontal: 30.0),
                            child: Text('Send to Store', style: TextStyle(color: Colors.white, fontSize: 20.0)),
                            onPressed: () {
                              sendCartList().then((res) {
                                if(res['status'] == 200) {

                                }
                              });
                            },
                          )
                      )
                    ],
                  )
              )
            )
          ],
        )
    );;
  }
}