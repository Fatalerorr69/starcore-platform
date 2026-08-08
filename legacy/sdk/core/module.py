#!/usr/bin/env python3

from datetime import datetime


class STARCOREModule:

    name="unknown"
    version="1.0"

    def install(self):
        return {
            "module":self.name,
            "action":"install",
            "status":"ok"
        }


    def start(self):
        return {
            "module":self.name,
            "action":"start",
            "status":"running"
        }


    def stop(self):
        return {
            "module":self.name,
            "action":"stop",
            "status":"stopped"
        }


    def health(self):
        return {
            "module":self.name,
            "health":"healthy",
            "timestamp":datetime.utcnow().isoformat()
        }


    def update(self):
        return {
            "module":self.name,
            "action":"update",
            "status":"updated"
        }


    def remove(self):
        return {
            "module":self.name,
            "action":"remove",
            "status":"removed"
        }
