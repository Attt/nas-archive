package io.github.attt.nasserver;

import com.google.gson.GsonBuilder;
import io.github.attt.nasserver.model.FileVo;
import io.github.attt.nasserver.service.FileService;
import org.junit.jupiter.api.Test;

import java.util.Set;

public class FileTests {

    FileService fileService = new FileService();

    @Test
    public void testFileVoTree() throws Throwable {
        Set<FileVo> roots = fileService.walk("/Users/atpex/Codes/attt.github.io/source","jp", "jpg", true);
//        printTree(roots, "");
        System.out.println(new GsonBuilder().excludeFieldsWithoutExposeAnnotation().create().toJson(roots));
    }
    private void printTree(Set<FileVo> fileVos, String intend){
        for(FileVo fileVo : fileVos){
            System.out.println(intend + "-" + (fileVo.isDir() ? "<dir>" : "") + fileVo.getName());
            if(fileVo.getChildren() != null) printTree(fileVo.getChildren(), intend + " ");
        }
    }
}
