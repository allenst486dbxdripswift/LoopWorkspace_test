//
//  CareSensShareClientPlugin.swift
//  CareSensShareClientPlugin
//
//  Created by Nathaniel Hamming on 2019-12-19.
//  Copyright © 2019 Mark Wilson. All rights reserved.
//

import os.log
import LoopKitUI
import CareSensShareClient
import CareSensShareClientUI

class CareSensShareClientPlugin: NSObject, CGMManagerUIPlugin {
    private let log = OSLog(category: "CareSensShareClientPlugin")
    
    public var cgmManagerType: CGMManagerUI.Type? {
        return CareSensShareClientManager.self
    }
    
    override init() {
        super.init()
        log.default("Instantiated")
    }
}
