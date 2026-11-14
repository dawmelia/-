import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '三国杀技能检索',
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xff4267b2),
      ),
      home: const SkillSearchPage(),
    );
  }
}

class SkillItem {
  final String name;
  final String hero;
  final String type;
  final String desc;
  SkillItem({required this.name, required this.hero, required this.type, required this.desc});
  factory SkillItem.fromList(List<String> cells) {
    return SkillItem(
      name: cells[0],
      hero: cells.length>1?cells[1]:"",
      type: cells.length>2?cells[2]:"",
      desc: cells.length>=4?(cells[4].isNotEmpty?cells[4]:cells[3]):"",
    );
  }
}

class SkillSearchPage extends StatefulWidget {
  const SkillSearchPage({super.key});
  @override
  State<SkillSearchPage> createState() => _SkillSearchPageState();
}

class _SkillSearchPageState extends State<SkillSearchPage> {
  List<SkillItem> skillList = [];
  List<SkillItem> filterList = [];
  TextEditingController searchCtrl = TextEditingController();
  bool loading = false;
  String tipText = "点击按钮拉取Bwiki图鉴";
  final String apiBase = "https://wiki.biligame.com/sgs/api.php";
  final String pageTitle = "技能图鉴";

  @override
  void initState() {
    super.initState();
    loadCache();
  }

  Future<void> loadCache() async {
    final sp = await SharedPreferences.getInstance();
    String? raw = sp.getString("skill_data");
    if(raw!=null){
      List<dynamic> jsonArr = jsonDecode(raw);
      setState(() {
        skillList = jsonArr.map((e)=>SkillItem(
          name:e["name"],hero:e["hero"],type:e["type"],desc:e["desc"]
        )).toList();
        filterList = List.from(skillList);
        tipText = "已加载本地缓存数据";
      });
    }
  }

  Future<void> saveCache() async {
    final sp = await SharedPreferences.getInstance();
    List<Map<String,String>> arr = skillList.map((e)=>{
      "name":e.name,"hero":e.hero,"type":e.type,"desc":e.desc
    }).toList();
    await sp.setString("skill_data", jsonEncode(arr));
  }

  Future<void> fetchWiki() async {
    setState(() {
      loading = true;
      tipText = "正在请求Bwiki...";
    });
    try{
      final params = {
        "action":"query",
        "titles":pageTitle,
        "prop":"revisions",
        "rvslots":"*",
        "rvprop":"content",
        "format":"json"
      };
      final uri = Uri.parse(apiBase).replace(queryParameters: params);
      final res = await http.get(uri);
      final js = jsonDecode(res.body);
      final pages = js["query"]["pages"];
      String pageKey = pages.keys.first;
      String wikitext = pages[pageKey]["revisions"][0]["slots"]["main"]["*"];
      parseWiki(wikitext);
      await saveCache();
      setState(() {
        tipText = "拉取成功，共${skillList.length}条技能";
        filterList = List.from(skillList);
      });
    }catch(e){
      setState(() {
        tipText = "拉取失败：$e";
      });
    }finally{
      setState(() {
        loading = false;
      });
    }
  }

  void parseWiki(String wt){
    skillList.clear();
    RegExp tableReg = RegExp(r'\{\|[\s\S]*?\|\}');
    var tables = tableReg.allMatches(wt);
    for(var m in tables){
      String tb = m.group(0)!;
      List<String> rows = tb.split(RegExp(r'\n\|-'));
      for(String row in rows){
        if(!row.contains('||')) continue;
        List<String> cells = row.split('||').map((s)=>
            s.replaceAll(RegExp(r'[\n\r\{\}\|]'),'').trim()
        ).where((s)=>s.isNotEmpty).toList();
        if(cells.length>=2){
          skillList.add(SkillItem.fromList(cells));
        }
      }
    }
    Map<String,bool> map = {};
    skillList = skillList.where((item){
      String k = "${item.name}|${item.hero}";
      if(map.containsKey(k)) return false;
      map[k]=true;
      return true;
    }).toList();
  }

  void onSearch(String kw){
    if(kw.trim().isEmpty){
      setState(()=>filterList=List.from(skillList));
      return;
    }
    String low = kw.toLowerCase();
    setState(() {
      filterList = skillList.where((s)=>
          s.name.toLowerCase().contains(low) || s.desc.toLowerCase().contains(low)
      ).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("三国杀技能检索")),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              children: [
                ElevatedButton(
                  onPressed: loading?null:fetchWiki,
                  child: const Text("拉取图鉴"),
                ),
                const SizedBox(width:10),
                Expanded(child: Text(tipText,style: const TextStyle(fontSize:12,color:Colors.grey)))
              ],
            ),
            const SizedBox(height:10),
            TextField(
              controller: searchCtrl,
              onChanged: onSearch,
              style: const TextStyle(color:Colors.white),
              decoration: const InputDecoration(
                labelText: "搜索技能名称/描述",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height:10),
            Expanded(
              child: filterList.isEmpty
                  ? const Center(child: Text("暂无数据"))
                  : ListView.builder(
                itemCount: filterList.length,
                itemBuilder: (ctx,idx){
                  SkillItem sk = filterList[idx];
                  return Card(
                    color: const Color(0xff272b33),
                    child: Padding(
                      padding: const EdgeInsets.all(10),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text("【${sk.name}】 ${sk.hero}",style: const TextStyle(fontSize:15,color:Color(0xffffdd88),fontWeight:FontWeight.bold)),
                          SizedBox(height:4),
                          Text("类型：${sk.type}",style: const TextStyle(fontSize:12,color:Colors.grey)),
                          SizedBox(height:4),
                          Text(sk.desc,style: const TextStyle(fontSize:13,color:Colors.white70)),
                        ],
                      ),
                    ),
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }
}
