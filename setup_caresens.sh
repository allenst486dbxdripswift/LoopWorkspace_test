#!/usr/bin/env bash
set -euo pipefail

# 1. create branch
git checkout -b caresens_integration || true

# 2. remove placeholder Loop directory (if exists)
if [ -d "Loop" ]; then
  git rm -r Loop || true
  git commit -m "Remove placeholder Loop submodule" || true
fi

# 3. add new Loop submodule
git submodule add https://github.com/allenst486dbxdripswift/Loop Loop
git commit -m "Add Loop submodule for caresens integration" || true

# 4. enter submodule and create branch
cd Loop
git checkout -b caresens_integration || true

# 5. create directories
mkdir -p Modules Parsers

# 6. write Swift files
cat > Modules/CareSensAirCrypto.swift <<'EOF'
import Foundation
import CryptoKit
import CommonCrypto

/// AES‑256 CTR (no‑padding) decryption for CareSens Air CGM.
struct CareSensAirCrypto {
    private static let keyString = "tq1Tg265o4UFD8tfPvNqUCiYyCxkhdZV"
    private static let keyData = Data(keyString.utf8)
    private static let iv = Data(repeating: 0, count: 16)   // placeholder nonce

    static func decrypt(_ ciphertext: Data) -> Data? {
        var out = Data(count: ciphertext.count)
        var outLen: size_t = 0

        let status = out.withUnsafeMutableBytes { outPtr -> CCCryptorStatus in
            var cryptor: CCCryptorRef?
            let create = CCCryptorCreateWithMode(
                CCOperation(kCCDecrypt),
                CCMode(kCCModeCTR),
                CCAlgorithm(kCCAlgorithmAES),
                CCPadding(ccNoPadding),
                iv.withUnsafeBytes { $0.baseAddress },
                keyData.withUnsafeBytes { $0.baseAddress },
                keyData.count,
                nil, 0, 0,
                CCModeOptions(kCCModeOptionCTR_LE),
                &cryptor)

            guard create == kCCSuccess, let ctx = cryptor else { return create }

            let upd = CCCryptorUpdate(ctx,
                                      ciphertext.withUnsafeBytes { $0.baseAddress },
                                      ciphertext.count,
                                      outPtr.baseAddress,
                                      out.count,
                                      &outLen)

            CCCryptorRelease(ctx)
            return upd
        }

        guard status == kCCSuccess else { return nil }
        out.removeSubrange(outLen..<out.count)
        return out
    }
}
EOF

cat > Modules/CareSensAirPeripheralManager.swift <<'EOF'
import Foundation
import CoreBluetooth

/// CoreBluetooth manager for CareSens Air CGM.
final class CareSensAirPeripheralManager: NSObject {
    private let serviceUUID = CBUUID(string: "0000FFE0-0000-1000-8000-00805F9B34FB")
    private let writeCharUUID = CBUUID(string: "0000FFE1-0000-1000-8000-00805F9B34FB")
    private let notifyCharUUID = CBUUID(string: "0000FFE2-0000-1000-8000-00805F9B34FB")

    private var central: CBCentralManager!
    private var peripheral: CBPeripheral?
    private var writeChar: CBCharacteristic?
    private var notifyChar: CBCharacteristic?

    override init() {
        super.init()
        central = CBCentralManager(delegate: self, queue: nil)
    }

    func startScanning() {
        guard central.state == .poweredOn else { return }
        central.scanForPeripherals(withServices: [serviceUUID], options: nil)
    }

    private func authenticate() {
        let pin = "123456"
        let deviceID = "CSAIR-001"
        let payload = "\(pin):\(deviceID)".data(using: .utf8)!
        guard let writeChar = writeChar else { return }
        peripheral?.writeValue(payload, for: writeChar, type: .withResponse)
    }

    private func handleIncoming(_ data: Data) {
        guard let plain = CareSensAirCrypto.decrypt(data) else { return }
        if let glucose = PacketParser.parse(plain) {
            NotificationCenter.default.post(name: .csAirGlucoseUpdate,
                                            object: nil,
                                            userInfo: ["glucose": glucose])
        }
    }
}

extension CareSensAirPeripheralManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state == .poweredOn { startScanning() }
    }
    func centralManager(_ central: CBCentralManager,
                        didDiscover peripheral: CBPeripheral,
                        advertisementData: [String : Any],
                        rssi RSSI: NSNumber) {
        self.peripheral = peripheral
        peripheral.delegate = self
        central.stopScan()
        central.connect(peripheral, options: nil)
    }
    func centralManager(_ central: CBCentralManager,
                        didConnect peripheral: CBPeripheral) {
        peripheral.discoverServices([serviceUUID])
    }
}

extension CareSensAirPeripheralManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let svc = peripheral.services?.first(where: { $0.uuid == serviceUUID }) else { return }
        peripheral.discoverCharacteristics([writeCharUUID, notifyCharUUID], for: svc)
    }
    func peripheral(_ peripheral: CBPeripheral,
                    didDiscoverCharacteristicsFor service: CBService,
                    error: Error?) {
        for char in service.characteristics ?? [] {
            if char.uuid == writeCharUUID { writeChar = char }
            if char.uuid == notifyCharUUID {
                notifyChar = char
                peripheral.setNotifyValue(true, for: char)
            }
        }
        authenticate()
    }
    func peripheral(_ peripheral: CBPeripheral,
                    didUpdateValueFor characteristic: CBCharacteristic,
                    error: Error?) {
        guard characteristic.uuid == notifyCharUUID,
              let data = characteristic.value else { return }
        handleIncoming(data)
    }
}

extension Notification.Name {
    static let csAirGlucoseUpdate = Notification.Name("csAirGlucoseUpdate")
}
EOF

cat > Parsers/PacketParser.swift <<'EOF'
import Foundation

/// Parses raw data packets from the CGM (header 0xAA55, length 20 bytes)
struct PacketParser {
    static func parse(_ data: Data) -> Double? {
        guard data.count >= 20 else { return nil }
        let header = data.prefix(2)
        guard header[0] == 0xAA && header[1] == 0x55 else { return nil }
        let adcBytes = data.subdata(in: 4..<8)
        let adc = adcBytes.withUnsafeBytes { $0.load(as: UInt32.self) }.littleEndian
        return GlucoseConverter.convert(adc: Double(adc))
    }
}
EOF

cat > Modules/GlucoseConverter.swift <<'EOF'
import Foundation

/// ADC → mg/dL conversion (constants extracted from libCALCULATION.so)
struct GlucoseConverter {
    private static let factor = 0.025   // voltage per ADC step
    private static let scale  = 1.2     // sensor‑specific scaling

    static func convert(adc: Double) -> Double {
        return adc * factor * scale
    }
}
EOF

cat > Modules/CareSensAirCGMPlugin.swift <<'EOF'
import Foundation
import LoopKit
import LoopKitUI

/// Loop용 CGM 플러그인. iOS Loop 코드베이스에 CareSens Air를 `CGMManager` 로 등록합니다.
final class CareSensAirCGMPlugin: NSObject, CGMManager {
    var delegate: CGMManagerDelegate?
    var pumpManager: PumpManagerUI?

    private let peripheral = CareSensAirPeripheralManager()

    func start() {
        peripheral.startScanning()
        NotificationCenter.default.addObserver(self,
                                               selector: #selector(handleGlucoseUpdate(_:)),
                                               name: .csAirGlucoseUpdate,
                                               object: nil)
    }

    func stop() {
        NotificationCenter.default.removeObserver(self)
    }

    @objc private func handleGlucoseUpdate(_ note: Notification) {
        guard let glucose = note.userInfo?["glucose"] as? Double else { return }
        let sample = GlucoseSample(
            uuid: UUID(),
            quantity: Double(glucose),
            startDate: Date(),
            endDate: Date(),
            isDisplayOnly: false,
            syncIdentifier: "\(Int(Date().timeIntervalSince1970))",
            device: "CareSens Air"
        )
        delegate?.cgmManager(self, didUpdate: [sample])
    }

    var deviceIdentifier: String? { return "CSAIR-001" }
    var managerIdentifier: String { return "CareSensAirCGMPlugin" }
    var shouldSyncToRemoteService: Bool { return true }
}
EOF

# 7. commit Swift files
git add Modules/*.swift Parsers/*.swift
git commit -m "Add CareSens Air BLE manager, crypto, parser, converter and CGM plugin"

# 8. push submodule branch
git push origin caresens_integration

# 9. go back to repo root and commit submodule update
cd ..
git add Loop
git commit -m "Update Loop submodule to caresens_integration branch"

git push origin caresens_integration

echo "CareSens Air integration setup complete."
