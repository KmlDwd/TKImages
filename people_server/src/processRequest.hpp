#pragma once

#include <opencv2/core/persistence.hpp>
#include <nlohmann/json.hpp>
#include <vector>
#include <string>
#include "PeopleDetector.hpp"


bool hasPeopleFilter(size_t numberOfPeople, bool hasPeople);
bool minPeopleFilter(size_t numberOfPeople, int minPeople);
bool maxPeopleFilter(size_t numberOfPeople, int maxPeople);

std::vector<std::string> filterImages(PeopleDetector&& peopleDetector,
                                      const std::vector<std::string>& paths,
                                      const nlohmann::json& options);

std::vector<std::string> processJsonRequest(const cv::FileStorage& cascadeFile,
                                            const nlohmann::json& reqJson);
std::vector<std::string> processJsonRequestParallel(const cv::FileStorage& cascadeFile,
                                                    const nlohmann::json& reqJson,
                                                    int threadsNumber = 6);