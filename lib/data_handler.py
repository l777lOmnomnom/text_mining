from warcio import ArchiveIterator, WARCWriter
from bs4 import BeautifulSoup
import sys


class Data:
    """
    This is the Data class which reads in the archive and returns an iterator with which you can go through all archive
    entries.
    """
    def __init__(self, source):
        self.source = source
        self.__archive = None
        self.__archive_stream = None

        self.__write_records = False  # This is a manual flag to enable writing of a test warc.gz archive

    def __iter__(self):
        """
        Returns an iterator of Data()

        :return: Iterator(Data)
        """
        return self

    def __next__(self):
        """
        Returns the next entry in the warc IO archive.

        :return: int(), str() - offset, text
        """
        tmp = list()
        __archive = open(self.source, "rb")
        __archive_stream = ArchiveIterator(__archive)

        wrong_encoding_list = list()

        current_element = 0
        for record in __archive_stream:
            # Extracts the responses
            if record.rec_type == 'response' and record.http_headers.get_header('Content-Type') in self.utf_8:
                soup = BeautifulSoup(record.content_stream(), 'lxml', from_encoding='utf-8')
                for script in soup(["script", "style"]):
                    script.extract()
                try:
                    text = soup.body.get_text(separator=' ')
                    text = "\n".join([line.strip() for line in text.split("\n") if line.strip() != ""])
                except AttributeError:
                    wrong_encoding_list.append(__archive_stream.get_record_offset())
                else:
                    # Prints the current element to command line if it is divisable by 100
                    if current_element % 100 == 0:
                        self.__clear_line()
                        print("{} elements hashed ...".format(current_element))


                    if current_element != 1000:
                        tmp.append(record)
                    elif current_element == 1000:
                        self.__write_example_archive(tmp)
                    else:
                        pass


                    current_element += 1
                    yield __archive_stream.get_record_offset(), text  # yields offset and text

        print('Wrong Encoding at offsets {}'.format(wrong_encoding_list))

    @property
    def utf_8(self):
        """
        This is the utf_8 encoding the DataHandler uses.

        :return: a list of utf8 encodings
        """
        return ['text/html; charset=UTF-8',
                'text/html; charset=utf-8',
                'text/html;charset=UTF-8',
                'text/html;charset=utf-8',
                'text/html; Charset=UTF-8',
                'text/html; Charset=utf-8;charset=UTF-8',
                'text/html; charset=utf8']

    @staticmethod
    def __clear_line():
        """
        This moves the cursor on the command line one line back and deletes the line.
        """
        sys.stdout.write("\033[F")  # back to previous line
        sys.stdout.write("\033[K")  # clear line

    @staticmethod
    def __write_example_archive(records):
        """

        :param records:
        :return:
        """

        with open("/tmp/test_archive.warc.gz", "rb") as archive:
            writer = WARCWriter(archive, gzip=True)
            for record in records:
                writer.write_record(record)
