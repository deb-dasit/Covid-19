import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import './home.dart';
import './menu.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SharedPreferences prefs = await SharedPreferences.getInstance();
  var token = prefs.getString('token');
  print(token);
  runApp(MaterialApp(
      title: 'Covid 19',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: token == null ? HomePage() : MenuPage()
  ));
}

//void main() => runApp(CovidApp());
//
//class CovidApp extends StatelessWidget {
//  // This widget is the root of your application.
//  @override
//  Widget build(BuildContext context) {
//    return MaterialApp(
//      title: 'Covid 19',
//      debugShowCheckedModeBanner: false,
//      theme: ThemeData(
//        primarySwatch: Colors.blue,
//      ),
//      home: HomePage(),
//    );
//  }
//}
