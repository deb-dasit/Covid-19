import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:web_socket_channel/io.dart';
import 'package:shared_preferences/shared_preferences.dart';

import './api.dart';
import './size_config.dart';

class ShopkeeperPage extends StatefulWidget {
  final void Function(int value) changeMenu;
  const ShopkeeperPage({Key key, this.changeMenu}) : super(key: key);
  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return _ShopkeeperPageState();
  }
}

class _ShopkeeperPageState extends State<ShopkeeperPage> {
  final storage = new FlutterSecureStorage();
  List _carts = [
    {
      "shop": "Balaji Stores",
      "location": "222, Kondapur, Hyderabad",
      "delivery": "211, Kondapur, Hyderabad"
    },
    {
      "shop": "Kundan Stores",
      "location": "187, Hafizpet, Hyderabad",
      "delivery": "Flat 202, Lakdikapul, Hyderabad"
    },
  ];

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
//    connectSocket();
//    getInitialData();
  }

//  connectSocket() {
//    IOWebSocketChannel.connect('ws://ec2-3-21-35-103.us-east-2.compute.amazonaws.com:8000/api/').stream.listen((data) {
//      Map response = json.decode(data);
//      if(response['eventType'] == 'Store status changed') {
//        for(var _store in _stores) {
//          if(_store['id'] == response['store_id']) {
//            setState(() {
//              _store['status'] = response['status'];
//            });
//          }
//        }
//      }
//    });
//  }

  getInitialData() async{
    Map<String, String> data = {};
    SharedPreferences prefs = await SharedPreferences.getInstance();
    var token = prefs.getString('token');
    Map<String, String> headers = {
      "Authorization": "token $token"
    };
    print(headers);
    final response = await http.get(Api.url+'/api/v1/allOrders', headers: headers);
    if(response.statusCode == 200) {
      Map responseJson = json.decode(response.body);
      if(responseJson['status'] == 200) {
        print(responseJson);
        setState(() {
          _carts = responseJson['cart'];
        });
      }
    } else {
      throw Exception("Failed to load post");
    }
  }


  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    SizeConfig().init(context);
    final List<Widget> _cartsList = new List<Widget>();
    for(var _cart in _carts) {
      print(_cart);
      _cartsList.add(
          Container(
            margin: EdgeInsets.symmetric(vertical: 20.0, horizontal: 20.0),
              padding: EdgeInsets.symmetric(vertical: 20.0, horizontal: 20.0),
              decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.all(Radius.circular(5.0)),
                  boxShadow: [new BoxShadow(
                    color: Colors.black.withOpacity(0.12),
                    blurRadius: 5.0,
                    offset:  Offset(
                      0.0, // Move to right 10  horizontally
                      3.0, // Move to bottom 10 Vertically
                    ),
                  ),]
              ),
            child: Column(
              children: <Widget>[
                Container(
                  margin:EdgeInsets.only(bottom:10.0),
                  alignment: Alignment.centerLeft,
                  child: Text('${_cart['shop']}', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20.0))
                ),
                Container(
                    margin:EdgeInsets.only(bottom:5.0),
                    alignment: Alignment.centerLeft,
                    child: Text('Pickup: ${_cart['location']}')
                ),
                Container(
                    alignment: Alignment.centerLeft,
                    child: Text('Delivery: ${_cart['delivery']}')
                )
              ],
            )
          )
      );
    }
    return Container(
        child: Column(
          children: <Widget>[
            Container(
              alignment: Alignment.centerLeft,
              padding: EdgeInsets.symmetric(vertical:SizeConfig.blockSizeVertical*2.0, horizontal:SizeConfig.blockSizeHorizontal*5.0),
              child: Text('Volunteer Pickups', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22.0)),
            ),
            Expanded(
                child: ListView(
                  shrinkWrap: true,
                  children: _cartsList,
                )
            )
          ],
        )
    );
  }
}