import { useState, useEffect } from 'react';
import firebase from 'firebase/compat/app';
import 'firebase/compat/firestore';


// Initialize Firebase
const firebaseConfig = {
  apiKey: 'YOUR_API_KEY',
  authDomain: 'YOUR_AUTH_DOMAIN',
  projectId: 'YOUR_PROJECT_ID',
  storageBucket: 'YOUR_STORAGE_BUCKET',
  messagingSenderId: 'YOUR_MESSAGING_SENDER_ID',
  appId: 'YOUR_APP_ID'
};

firebase.initializeApp(firebaseConfig);

const db = firebase.firestore();

function App() {
  const [rssList, setRssList] = useState([]);
  const [newRssUrl, setNewRssUrl] = useState('');

  useEffect(() => {
    const unsubscribe = db.collection('rss').onSnapshot(snapshot => {
      const rssData = [];
      snapshot.forEach(doc => {
        rssData.push({ id: doc.id, ...doc.data() });
      });
      setRssList(rssData);
    });
    return unsubscribe;
  }, []);

  const handleAddRss = async () => {
    if (newRssUrl.trim() !== '') {
      await db.collection('rss').add({ url: newRssUrl });
      setNewRssUrl('');
    }
  };

  return (
    <div>
      <h1>My RSS Reader</h1>
      <input
        type="text"
        value={newRssUrl}
        onChange={e => setNewRssUrl(e.target.value)}
        placeholder="Enter RSS URL"
      />
      <button onClick={handleAddRss}>Add RSS</button>
      <ul>
        {rssList.map(rss => (
          <li key={rss.id}>{rss.url}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
