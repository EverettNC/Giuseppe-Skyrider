import React from 'react';
import { Instagram, Twitter, Linkedin, Send } from 'lucide-react';
// "Nothing Vital Lives Below Root" - Imports corrected
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';

export default function GiovanniSocialMedia() {
  return (
    <Card className="bg-gray-950 border-gray-800">
      <CardHeader>
        <CardTitle className="italic uppercase">Social Reach</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        <Button variant="outline" className="border-gray-800 text-gray-400 hover:text-white">
          <Instagram className="w-4 h-4 mr-2" /> Instagram
        </Button>
        <Button variant="outline" className="border-gray-800 text-gray-400 hover:text-white">
          <Twitter className="w-4 h-4 mr-2" /> X / Twitter
        </Button>
      </CardContent>
    </Card>
  );
}
