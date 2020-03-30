import 'package:flutter/material.dart';

import './store_list.dart';
import './cart.dart';
import './shopkeeper.dart';

void main() => MenuPage();

class MenuPage extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    // TODO: implement createState
    return _MenuPageState();
  }
}

class _MenuPageState extends State<MenuPage> {
  int _selectedIndex = 0;

  _onNavBarItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Scaffold(
//      appBar: AppBar(
//        title: Text('Covid-19'),
//      ),
      bottomNavigationBar: BottomNavigationBar(
        items: <BottomNavigationBarItem> [
          BottomNavigationBarItem(
            icon: Icon(Icons.store),
            title: Text('Stores')
          ),
          BottomNavigationBarItem(
              icon: Icon(Icons.shopping_cart),
              title: Text('Cart')
          ),
          BottomNavigationBarItem(
              icon: Icon(Icons.account_circle),
              title: Text('Shopkeeper')
          )
        ],
        currentIndex: _selectedIndex,
        onTap: _onNavBarItemTapped,
      ),
      body: SafeArea(
        child: _selectedIndex == 0
            ?
        StoreListPage(key: PageStorageKey('StoreList'), changeMenu: _onNavBarItemTapped)
        :
        _selectedIndex == 1 ?
        CartPage(key: PageStorageKey('Cart'))
        :
        ShopkeeperPage(key: PageStorageKey('Shop')),
      ),
    );
  }
}