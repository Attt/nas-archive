package io.github.attt.nasserver;


import com.apptasticsoftware.rssreader.RssReader;
import okhttp3.*;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class OkhttpTests {

    OkHttpClient client = new OkHttpClient();

    @Test
    public void whenAsynchronousGetRequest_thenCorrect() throws InterruptedException {
        Request request = new Request.Builder()
                .url("https://mikanani.me/RSS/Bangumi?bangumiId=2750")
                .build();

        Call call = client.newCall(request);
        call.enqueue(new Callback() {
            public void onResponse(Call call, Response response)
                    throws IOException {
                //System.out.println(response.body().string());

            }

            public void onFailure(Call call, IOException e) {
                fail();
            }
        });

        TimeUnit.SECONDS.sleep(10);
    }

    private void fail(){
        System.out.println("failed to request");
    }
}
