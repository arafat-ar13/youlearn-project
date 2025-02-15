export const extractPdfText = async (url: string) => {
    try {
      // URL needs to be encoded since it's part of the path
      const encodedUrl = encodeURIComponent(url);
      const response = await fetch(`http://localhost:8000/extract/${encodedUrl}`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  };