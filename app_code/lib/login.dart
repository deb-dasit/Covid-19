import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import './menu.dart';
import './api.dart';
import './signup.dart';
import './size_config.dart';

void main() => LoginPage();

class LoginPage extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return _LoginPageState();
  }
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  Future<Map> login() async {
    var map = new Map<String, dynamic>();
    map["username"] = _usernameController.text;
    map["password"] = _passwordController.text;
    final response = await http.post(Api.url+'/api/v1/login', body: map);
    if(response.statusCode == 200) {
      Map responseJson = json.decode(response.body);
      print(responseJson);
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
                  child: Text('Login', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22.0)),
                ),
                Container(
                  padding: EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*1.5, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                  child: TextField(
                    controller: _usernameController,
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
                  child: TextField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: InputDecoration(
                          hintText: 'Password',
                          contentPadding: EdgeInsets.fromLTRB(15.0, 15.0, 15.0, 15.0),
                          border: new OutlineInputBorder(
                              borderRadius: new BorderRadius.circular(25.0),
                              borderSide: new BorderSide(
                              )
                          )
                      )
                  )
                ),
                Container(
                  width: SizeConfig.blockSizeHorizontal*100,
                  padding:EdgeInsets.symmetric(vertical: SizeConfig.blockSizeVertical*2.0, horizontal: SizeConfig.blockSizeHorizontal*5.0),
                  child: MaterialButton(
                      color: Color(0xff5D6D7E),
                      elevation: 2.0,
                      padding: EdgeInsets.symmetric(vertical: 20.0, horizontal: 30.0),
                    onPressed: () {
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
                    child: Text('LOGIN', style: TextStyle(fontSize: 18.0, color: Colors.white))
                  )
                ),
                Material(
                    child: MaterialButton(
                        onPressed: () {
                          Navigator.push(
                              context,
                              MaterialPageRoute(builder: (context) => SignupPage())
                          );
                        },
                        child: Text('Go To Signup')
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