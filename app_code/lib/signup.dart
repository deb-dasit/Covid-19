import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import './menu.dart';
import './api.dart';
import './login.dart';
import './size_config.dart';

void main() => SignupPage();

class SignupPage extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return _SignupPageState();
  }
}

class _SignupPageState extends State<SignupPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  final _storeController = TextEditingController();
  final _addressController = TextEditingController();
  final _localityController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _pinController = TextEditingController();
  String _role = 'user';
  Future<Map> login() async {
    var map = new Map<String, dynamic>();
    map["name"] = _nameController.text;
    map["email"] = _emailController.text;
    map["password"] = _passwordController.text;
    map["role"] = _role;
    if(_role == 'shopkeeper'){
      map["shop_name"] = _storeController.text;
      map["address"] = _addressController.text;
      map["locality"] = _localityController.text;
      map["city"] = _cityController.text;
      map["state"] = _stateController.text;
      map["pincode"] = _pinController.text;
    }
    print(map);
    final response = await http.post(Api.url+'/api/v1/signup', body: map);
    if(response.statusCode == 200) {
      Map responseJson = json.decode(response.body);
      return responseJson;
    } else {
      throw Exception("Failed to load post");
    }
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    SizeConfig().init(context);
    return Scaffold(
      body: SafeArea(
          child: SingleChildScrollView(
              child: Container(
                  child: Column(
                    children: <Widget>[
                      Container(
                        alignment: Alignment.centerLeft,
                        padding: EdgeInsets.symmetric(vertical:SizeConfig.blockSizeVertical*2.0, horizontal:SizeConfig.blockSizeHorizontal*5.0),
                        child: Text('Signup', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22.0)),
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                          controller: _nameController,
                          obscureText: false,
                          decoration: InputDecoration(
                              hintText: 'Full Name',
                              contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                              border: new OutlineInputBorder(
                                  borderRadius: new BorderRadius.circular(25.0),
                                  borderSide: new BorderSide(
                                  )
                              )
                          ),
                        ),
                      ),
                      Container(
                          padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                          child:TextField(
                            controller: _emailController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'Email Address',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            ),
                          ),
                      ),
                      Container(
                          padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                          child:TextField(
                              controller: _passwordController,
                              obscureText: true,
                              decoration: InputDecoration(
                                  hintText: 'Password',
                                  contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                  border: new OutlineInputBorder(
                                      borderRadius: new BorderRadius.circular(25.0),
                                      borderSide: new BorderSide(
                                      )
                                  )
                              )
                          ),
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
                                    value: 'user',
                                    groupValue: _role,
                                    onChanged: (value) {
                                      setState(() { _role = value; });
                                    },
                                  ),
                                  Text('User')
                                ],
                              ),
                            ),
                            Container(
                              child: Row(
                                children: <Widget>[
                                  Radio(
                                    value: 'volunteer',
                                    groupValue: _role,
                                    onChanged: (value) {
                                      setState(() { _role = value; });
                                    },
                                  ),
                                  Text('Volunteer')
                                ],
                              )
                            ),
                            Container(
                              child: Row(
                                children: <Widget>[
                                  Radio(
                                    value: 'shopkeeper',
                                    groupValue: _role,
                                    onChanged: (value) {
                                      setState(() { _role = value; });
                                    },
                                  ),
                                  Text('Shopkeeper')
                                ],
                              )
                            ),
                          ],
                        ),
                      ),
                      _role == 'shopkeeper' ? Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                            controller: _storeController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'Store Name',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            )
                        ),
                      ) : Container(),
                      _role == 'shopkeeper' ? Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                            controller: _addressController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'Address',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            )
                        ),
                      ) : Container(),
                      _role == 'shopkeeper' ? Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                            controller: _localityController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'Locality',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            )
                        ),
                      ) : Container(),
                      _role == 'shopkeeper' ? Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                            controller: _cityController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'City',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            )
                        ),
                      ) : Container(),
                      _role == 'shopkeeper' ? Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                            controller: _stateController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'State',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            )
                        ),
                      ) : Container(),
                      _role == 'shopkeeper' ? Container(
                        padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                        child:TextField(
                            controller: _pinController,
                            obscureText: false,
                            decoration: InputDecoration(
                                hintText: 'Pin Code',
                                contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 10.0),
                                border: new OutlineInputBorder(
                                    borderRadius: new BorderRadius.circular(25.0),
                                    borderSide: new BorderSide(
                                    )
                                )
                            )
                        ),
                      ) : Container(),
                      Container(
                          width: SizeConfig.blockSizeHorizontal*100,
                          padding:EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*2.0, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                          child: MaterialButton(
                              color: Color(0xff5D6D7E),
                              elevation: 2.0,
                              padding: EdgeInsets.symmetric(vertical: 20.0, horizontal: 30.0),
                              onPressed: () {
//                                Navigator.push(
//                                    context,
//                                    MaterialPageRoute(builder: (context) => MenuPage())
//                                );
                                login().then((res) async{
                                  if(res['status'] == 200) {
                                    SharedPreferences prefs = await SharedPreferences.getInstance();
                                    prefs.setString('token', res['access_token']);
                                    Navigator.push(
                                        context,
                                        MaterialPageRoute(builder: (context) => MenuPage())
                                    );
                                  }
                                });
                              },
                              child: Text('SIGNUP', style: TextStyle(fontSize: 18.0, color: Colors.white))
                          )
                      ),
                      Material(
                          child: MaterialButton(
                              onPressed: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(builder: (context) => LoginPage())
                                );
                              },
                              child: Text('Go To Login')
                          )
                      )
                    ],
                  )
              )
          )
      ),
    );
  }
}