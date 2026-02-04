from difflib import get_close_matches
import xml.etree.ElementTree as ET
from typing import Any, Dict

from globals.consts.const_strings import ConstStrings
from infrastructure.interfaces.iconfig_manager import IConfigManager
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.logger_messages import LoggerMessages


class XMLConfigManager(IConfigManager):
    def __init__(self, xml_path: str) -> None:
        self.config_path = xml_path
        self.root = self._load_xml()
        self._logger = LoggerFactory.get_logger_manager()
        if isinstance(self.root, ET.ElementTree):
            self.root = self.root.getroot()

    def get(self, *path: str) -> Any:
        current = self.root
        if len(path) == 1:
            for element in self._get_all_xml_elements(current):
                if element.text and element.text.strip() == path[0]:
                    return element.text.strip()
            return None
        for key in path:
            if current is None:
                return None
            current = current.find(key)
        if current is not None and current.text is not None:
            return current.text.strip()
        return None

    def set(self, *path: str, value: Any) -> None:
        current = self.root
        for key in path[:-1]:
            next_element = current.find(key)
            if next_element is None:
                next_element = ET.SubElement(current, key)
            current = next_element
        # ? Update or create the final element
        last_key = path[-1]
        final_element = current.find(last_key)
        if final_element is None:
            final_element = ET.SubElement(current, last_key)
        final_element.text = str(value)

    def exists(self, *path: str) -> bool:
        current = self.root
        for key in path:
            all_elements = self._get_all_xml_elements(current)
            # ? Searches for the key in the content of all elements
            next_element = None
            for element in all_elements:
                if element.text and key == element.text.strip():
                    next_element = element
                    break
            if next_element is None:
                self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                                 LoggerMessages.CONFIG_KEY_NOT_FOUND.format(key))
                # ? Suggest the closest match
                most_likely = None
                close_matches = get_close_matches(
                    key, [el.text.strip() for el in all_elements if el.text], n=1, cutoff=0.6)
                if close_matches:
                    most_likely = close_matches[0]
                if most_likely:
                    self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                                     LoggerMessages.CONFIG_DID_YOU_MEAN.format(most_likely))
                else:
                    self._logger.log(ConstStrings.LOG_NAME_DEBUG,
                                     LoggerMessages.CONFIG_NO_MATCHES)
                return False
            current = next_element
        return True

    def get_all(self) -> Dict[str, Any]:
        def element_to_dict(element: ET.Element) -> Dict[str, Any]:
            if not list(element):
                return element.text.strip() if element.text else None
            return {child.tag: element_to_dict(child) for child in element}
        return {self.root.tag: element_to_dict(self.root)}

    def _get_all_xml_elements(self, element: Any) -> list:
        elements = []
        for child in element:
            elements.append(child)
            elements.extend(self._get_all_xml_elements(child))
        return elements

    def _load_xml(self) -> ET.Element:
        try:
            tree = ET.parse(self.config_path)
            return tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"{self.config_path}': {e}")
