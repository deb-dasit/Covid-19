import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:web_socket_channel/io.dart';
import 'package:shared_preferences/shared_preferences.dart';

import './api.dart';
import './size_config.dart';

class StoreListPage extends StatefulWidget {
  final void Function(int value) changeMenu;
  const StoreListPage({Key key, this.changeMenu}) : super(key: key);
  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return _StoreListPageState();
  }
}

class _StoreListPageState extends State<StoreListPage> {
  final storage = new FlutterSecureStorage();
  List _stores = [
    {
      "id": 1,
      "name": "Balaji Stores",
      "owner_id": "Durga Prasad",
      "status": true
    },
    {
      "id": 2,
      "name": "Kundan Stores",
      "owner_id": "Hari Prasad",
      "status": true
    },
    {
      "id": 3,
      "name": "Ratnadeep",
      "owner_id": "Ratnadeep and sons",
      "status": false
    }
  ];

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
//    connectSocket();
//    getInitialData();
  }

  connectSocket() {
    IOWebSocketChannel.connect('ws://ec2-3-21-35-103.us-east-2.compute.amazonaws.com:8000/api/').stream.listen((data) {
      Map response = json.decode(data);
      if(response['eventType'] == 'Store status changed') {
        for(var _store in _stores) {
          if(_store['id'] == response['store_id']) {
            setState(() {
              _store['status'] = response['status'];
            });
          }
        }
      }
    });
  }

  getInitialData() async{
    Map<String, String> data = {};
    SharedPreferences prefs = await SharedPreferences.getInstance();
    var token = prefs.getString('token');
    Map<String, String> headers = {
      "Authorization": "token $token"
    };
    print(headers);
    final response = await http.get(Api.url+'/api/v1/shops', headers: headers);
    if(response.statusCode == 200) {
      Map responseJson = json.decode(response.body);
      if(responseJson['status'] == 200) {
        print(responseJson);
        setState(() {
          _stores = responseJson['shops'];
        });
      }
    } else {
      throw Exception("Failed to load post");
    }
  }

  selectStore(id) async {
    for(var _store in _stores) {
      if(_store["id"] == id && _store["status"] == true) {
        await storage.write(key: 'selectedStore', value: id.toString());
        widget.changeMenu(1);
        return true;
      }
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    SizeConfig().init(context);
    final List<Widget> _storesList = new List<Widget>();
    for(var _store in _stores) {
      _storesList.add(
        InkWell(
          onTap: () {
            if(selectStore(_store["id"]) == false) {
              print('cant go there bruh');
            }
          },
          child: Container(
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
            margin: EdgeInsets.symmetric(horizontal: SizeConfig.blockSizeHorizontal*5.0, vertical: SizeConfig.blockSizeVertical*1.5),
            padding:EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*2.5, horizontal: SizeConfig.blockSizeHorizontal*10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: <Widget>[
                  Flexible(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(_store["name"], overflow: TextOverflow.ellipsis, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18.0),),
                        Text(_store["owner_id"].toString(), style: TextStyle(color:Color(0xffB2BABB)))
                      ],
                    ),
                  ),
                  Icon(Icons.brightness_1, size: 15.0, color: _store["status"] == true ? Color(0xff2ECC71) : Color(0xffE74C3C))
                ],
              )
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
            child: Text('Stores List', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22.0)),
          ),
          Expanded(
            child: ListView(
              shrinkWrap: true,
              children: _storesList,
            )
          )
        ],
      )
    );
  }
}