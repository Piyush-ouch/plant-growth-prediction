# 🌿 Plant Growth Prediction - Flutter Integration Guide

This guide will help you connect your **Python Backend** to your **Flutter App**.

## 1️⃣ Add Dependencies
Open your `pubspec.yaml` file and add these packages:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0          # For making API calls
  image_picker: ^1.0.7  # For taking photos
```

Run `flutter pub get` in your terminal.

---

## 2️⃣ Create the API Service
Create a new file `lib/services/growth_service.dart`.
This handles sending the image and crop name to your backend.

**Important for Android Emulator:** use `10.0.2.2` instead of `127.0.0.1`.

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class GrowthService {
  // -------------------------------------------------------------
  // FOR REAL PHONE (ANDROID/iOS):
  // 1. Connect Phone & PC to the SAME Wi-Fi.
  // 2. Find PC IP: Run `ipconfig` (Windows) or `ifconfig` (Mac/Linux).
  // 3. Replace below with YOUR PC IP (e.g. 192.168.1.5).
  static const String baseUrl = "http://192.168.X.X:5000/predict";
  
  // FOR ANDROID EMULATOR (if testing on PC):
  // static const String baseUrl = "http://10.0.2.2:5000/predict";
  // -------------------------------------------------------------

  static Future<Map<String, dynamic>?> predictStage(File imageFile, String crop) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse(baseUrl));
      
      // Add the Crop Name
      request.fields['crop'] = crop;

      // Add the Image File
      request.files.add(await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
      ));

      // Send Request
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print("Server Error: ${response.body}");
        return null;
      }
    } catch (e) {
      print("Error sending prediction request: $e");
      return null;
    }
  }
}
```

---

## 3️⃣ Create the UI Screen
Create a file `lib/screens/growth_screen.dart`.
This screen allows the farmer to:
1. Select a Crop.
2. Take a Photo.
3. See Results.

```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/growth_service.dart';

class GrowthScreen extends StatefulWidget {
  @override
  _GrowthScreenState createState() => _GrowthScreenState();
}

class _GrowthScreenState extends State<GrowthScreen> {
  File? _image;
  final picker = ImagePicker();
  String _selectedCrop = "Tomato";
  Map<String, dynamic>? _result;
  bool _loading = false;

  final List<String> _crops = ["Tomato", "Wheat", "Rice"];

  // Pick Image from Camera
  Future getImage() async {
    final pickedFile = await picker.pickImage(source: ImageSource.camera);

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _result = null; // Reset previous result
      });
    }
  }

  // Call Backend API
  Future analyzeImage() async {
    if (_image == null) return;

    setState(() {
      _loading = true;
    });

    var res = await GrowthService.predictStage(_image!, _selectedCrop);

    setState(() {
      _result = res;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("🌱 Plant Growth AI")),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(20),
        child: Column(
          children: [
            // 1. Crop Selection Dropdown
            DropdownButtonFormField<String>(
              value: _selectedCrop,
              decoration: InputDecoration(
                labelText: "Select Crop",
                border: OutlineInputBorder(),
              ),
              items: _crops.map((String crop) {
                return DropdownMenuItem<String>(
                  value: crop,
                  child: Text(crop),
                );
              }).toList(),
              onChanged: (newValue) {
                setState(() {
                  _selectedCrop = newValue!;
                });
              },
            ),
            SizedBox(height: 20),

            // 2. Image Display Area
            Container(
              height: 250,
              width: double.infinity,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(10),
              ),
              child: _image == null
                  ? Center(child: Text("No image selected"))
                  : Image.file(_image!, fit: BoxFit.cover),
            ),
            SizedBox(height: 20),

            // 3. Action Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: getImage,
                  icon: Icon(Icons.camera_alt),
                  label: Text("Take Photo"),
                ),
                ElevatedButton.icon(
                  onPressed: _loading ? null : analyzeImage,
                  icon: Icon(Icons.analytics),
                  label: Text(_loading ? "Analyzing..." : "Analyze"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 30),

            // 4. Result Display
            if (_result != null) ...[
              Divider(),
              Text(
                "Prediction Result",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 10),
              _buildResultCard(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    String stage = _result!['growth_stage'];
    int confidence = _result!['confidence'];
    double ratio = _result!['green_ratio'];

    Color statusColor = confidence > 80 ? Colors.green : Colors.orange;

    return Card(
      elevation: 4,
      color: Colors.white,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              stage,
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.green),
            ),
            Text("Growth Stage"),
            SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Confidence: $confidence%"),
                Text("Coverage: ${(ratio * 100).toStringAsFixed(1)}%"),
              ],
            ),
            SizedBox(height: 10),
            if (confidence < 70)
              Container(
                padding: EdgeInsets.all(8),
                color: Colors.orange.shade100,
                child: Row(
                  children: [
                    Icon(Icons.warning, color: Colors.orange),
                    SizedBox(width: 8),
                    Expanded(child: Text("Result unsure. Please ensure good lighting and clear view.")),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

---

## 4️⃣ Running It
1.  **Start Python Server**:
    Make sure your `app.py` is running (`python app.py`).
2.  **Start Android Emulator**.
3.  **Run Flutter App**: `flutter run`.
4.  Select a crop, take a photo (or pick from gallery if you modify the picker), and click **Analyze**.

✅ The app calls `http://10.0.2.2:5000/predict` and displays the stage!
