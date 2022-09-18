package io.github.attt.nasserver;

import com.apptasticsoftware.rssreader.Item;
import com.apptasticsoftware.rssreader.RssReader;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class RssTests {

    RssReader reader = new RssReader();

    @Test
    public void testRssReader() throws IOException {
        Stream<Item> rssFeed = reader.read("https://mikanani.me/RSS/Bangumi?bangumiId=2750");
        List<Item> items = rssFeed.toList();
        for (Item item : items) {
            System.out.println(item);
        }
    }
}
